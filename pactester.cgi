#!/usr/bin/perl -T

# Author:  (c) 2013 Bennett Perkins
#
#
# Copyright 2013 Bennett Perkins
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

use POSIX;
use English qw(-no_match_vars);
use CGI qw/:standard remote_addr/;
use CGI::Carp;
use File::Fetch;
use URI;
use strict;
use warnings;

# untaint the environment
delete @ENV{qw(PATH IFS CDPATH ENV BASH_ENV)};

# try to prevent proxy use
delete @ENV{qw(http_proxy HTTP_PROXY
		https_proxy HTTPS_PROXY
		ftp_proxy FTP_PROXY
		proxy PROXY
		rtsp_proxy RTSP_PROXY)};

# defaults
my $default_pac = 'http://wpad.com/wpad.dat';
my $default_url = 'http://www.google.com';
my $default_ip  = '10.25.64.100';

# constants
my $sp = ' ';
my $nbsp = '&nbsp;';
my $tab = "\t";
my $nbtab = $nbsp x 4;
my $da = '-';
my $nbda = '&#x2011;';

# params
my $pac = param('pac');
my $pac_tainted = $pac;
my $url = param('url');
my $ip  = param('ip');
my $ex  = param('ex');
my $sub = param('submit');

# untaint the params
if ($pac) { 
	my $uri = URI->new($pac);
	if(defined($uri->scheme) and $uri->scheme =~ /http/) {
		$pac = $uri->as_string;
	} else {
		$pac = 'bad';
	}
} else {
	$pac = $default_pac;
}

if ($url) {
	my $uri = URI->new($url);
	unless (defined($uri->scheme)) {
		$uri = URI->new("http://$url"); #let's get retarded
	}
	if($uri->scheme =~ /http/i or $uri->scheme =~ /ftp/i) {
		$url = $uri->as_string;
	} else {
		if ($url =~ /([a-zA-Z0-9\$-_\+\!()*\/?\&]*)/) {
			$url = $1;
		} else {
			$url = 'bad';
		}
	}
} else {
	$url = $default_url;
}
my $url_host = ( URI->new($url)->can('host') ? URI->new($url)->host : undef );

my $new_default_ip = remote_addr;
if (($new_default_ip) and ($new_default_ip ne '127.0.0.1')) {
	$default_ip = $new_default_ip;
}

if (!$ip) {
	$ip = $default_ip;
}
if ($ip) {
	if ($ip =~ /([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/) {
		$ip = $1;
	} else {
		$ip = 'bad';
	}
} else {
	$ip = '';
}

if ($ex) {
	if ($ex =~ /(on)/) {
		$ex = $1;
	} else {
		$ex = '';
	}
} else { 
	$ex = '';
}

if ($sub) {
	if ($sub =~ /(Submit)/) {
		$sub = $1;
	} else {
		$sub = '';
	}
} else {
	$sub = '';
}

# sylesheet
my $css = q/
	body {
		color: black;
		background-color: white;
		font-family: sans-serif, serif;
		font-weight: normal;
		font-size: 9pt;
		overflow-y: scroll;
	}

	h1 {
		font-size: 4em;
		padding-top: 0.5em;
	}

	a, a:hover, a:visited, a:active, a:focus {
		color: darkblue;
	}

	.result {
		font-family: monospace, serif;
		font-size: 12pt;
		margin-top:     0;
		padding-top:    1pt;
		padding-bottom: 40pt;
	}

	.result_h {
		margin-bottom:  0;
		padding-top:    20pt;
	}

	.result_s {
		padding-top:    0;
		padding-bottom: 0;
		margin-top:     0;
		margin-bottom:  0;
		overflow-x: hidden;
	}

	.error {
		padding-tom: 5pt;
		padding-bottom: 15pt;
		color: red;
	}

	input[type="text"] {
		width: 100%;
	}

	div {
		padding: 0;
		border: none;
		margin-top: 0;
		margin-bottom: 0;
	}

	div, p, hr, h1 {
		width: 60%;
		margin-left:  auto;
		margin-right: auto;
		display: block;
	}

	pre {
		background-color: #eee;
		padding: 2px;
		border: 1px #bbb solid;
		overflow-x: auto;
	}

	hr {
		color: darkgray;
		background-color: darkgray;
		border: 0;
		height: 1px;
	}

	@media (max-width:680px) {
		h1 {
			font-size: 3em;
			padding-top: 0.4em;
		}
		div, p, hr, h1 {
			width: 80%;
		}
		.result_h {
			padding-top:    20pt;
		}
		.result {
			padding-bottom: 25pt;
		}
	}

	@media (max-width:520px) {
		h1 {
			font-size: 2em;
			padding-top: 0.3em;
		}
		div, p, hr, h1 {
			width: 95%;
		}
		.result_h {
			padding-top:    10pt;
		}
		.result {
			padding-bottom: 15pt;
		}
	}
/;

# show pacfile contents
my $toggle_pacview = q[
  function toggle_view(id)
  {
    var e = document.getElementById(id);
    if (e != null)
    {
      e.style.display = ( e.style.display != 'none' ? 'none' : '' );
    }
  }
  function hide_view(id)
  {
    var e = document.getElementById(id);
    if (e != null)
    {
      e.style.display = 'none';
    }
  }
];

# start printing the html doc
print header('text/html'),
	start_html(-title=>'pactester',	-style=>{-code=>$css}, -script=>$toggle_pacview),
	h1('pactester'),
	start_form(-method=>'POST'),p,
	'PAC to test: ', textfield(-name=>'pac', -value=>$pac),p,
	'Hostname or URL to test: ', textfield(-name=>'url', -value=>$url),p,
	'Client IP: ', textfield(-name=>'ip', -value=>$ip),p,
	checkbox(-name=>'ex', -checked=>0, -value=>'on', -label=>'Enable Microsoft Extensions'),p,
	submit(-name=>'submit', value=>'Submit'),
	end_form,
	hr;

# launch pactester if form was submitted
if($sub) {

	# fetch pacfile
	my $ff = File::Fetch->new(uri => $pac);
	if (!$ff) {
		print p({class=>'error'},"Error: Bad PAC: $pac_tainted ($!)"),hr;
		goto DONE;
	}
	my $where = $ff->fetch(to=>'/tmp');
	my $pac_contents = '';
	if (!$where) {
		print p({class=>'error'},"Error: Could not fetch PAC file: $pac_tainted ($!)"),hr;
		goto DONE;
	} else {
		open(PAC_CONTENTS, '<'.$where) or die "Can't read PAC file: $!";
		while (<PAC_CONTENTS>) {
			$pac_contents .= $_;
		}
		close PAC_CONTENTS;
	}
	
	# -e arg
	my $exarg = '';
	if ($ex eq 'on') {
		$exarg = '-e';
	}

	# -c clientip arg
	my $iparg = '';
	if ($ip) {
		$iparg = '-c';
	}

	# fork a child process to handle pactester launch
	die "Can't fork: $!" unless defined(my $pactester_pid = open(RESULT, '-|'));
	if (!$pactester_pid) {		# child
	
		# redirect stderr
		open(STDERR, '>&STDOUT');

		# launch pactester
		exec '/usr/bin/pactester',
			'-p', $where,
			'-u', $url,
			$exarg,
			$iparg, $ip
				or die 'exec failed!';
	
		# child is done!
		exit 0;
	}

	# fork another child process to get url info
	die "Can't fork: $!" unless defined(my $urlinfo_pid = open(URLINFO_OUTPUT, '-|'));
	if (!$urlinfo_pid) {		# child

		# redirect stderr
		open(STDERR, '>&STDOUT');

		if ($url_host) {
			if ($url_host =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\.?$/) {
				exec '/usr/bin/dig','-x',$url_host,'IN','PTR' or die 'exec failed!';
			} else {
				exec '/usr/bin/dig', $url_host or die 'exec failed!';
			}
		} else {
			print 'No further information available.';
		}

		# child is done!
		exit 0;
	}

	# print summary
	print p,p({-class=>'result_s'},qq'PAC:&nbsp;<a onclick='.
			qq'"hide_view(\'urlview\'); toggle_view(\'pacview\')" href="#">$pac</a>'),
		p({-class=>'result_s'},qq'URL:&nbsp;<a onclick='.
			qq'"hide_view(\'pacview\'); toggle_view(\'urlview\')" href="#">$url</a>'),
		p({-class=>'result_s'},"Client IP:&nbsp;$ip");
	if ($exarg) { print p({-class=>'result_s'},'Microsoft Extensions enabled.'); }
	print p;

	# read url info from child
	my $urlinfo_output = '';
	while(<URLINFO_OUTPUT>) {
		$urlinfo_output .= $_;
	}
	close URLINFO_OUTPUT;

	# hidden elements for url info and pacfile info
	print div({id=>'urlview',-style=>'display:none'},pre(code($urlinfo_output))),
		div({id=>'pacview',-style=>'display:none'},pre(code($pac_contents))),p;

	# read result, add <br> on newline, replace spaces with &nbsp;, etc.
	my $result = '';
	while (<RESULT>) {
		$_ =~ s/$sp/$nbsp/g;
		$_ =~ s/$tab/$nbtab/g;
		$result .= $_.br;
	}

	# print result
	print p({-class=>'result_h'},'Result: '),p,
		div(pre({-class=>'result'},"<code>$result</code>")),p,hr;
	close RESULT;

	# remove tempfile
	unless (unlink($where)) {
		carp "Warning: Could not delete temp file $where";
	}
}

DONE:

# about
print p,'This tool uses the pactester&nbsp;utility by Manu&nbsp;Garg (available ',
		a({href=>'https://code.google.com/p/pacparser/'},'here'),').',p;

# parent is done!
print end_html;
exit 0;
