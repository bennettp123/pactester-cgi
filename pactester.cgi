#!/usr/bin/perl -T

# Author:  (c) 2013 Bennett Perkins

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

# defaults
my $default_pac = 'http://isd.det.wa.edu.au/isd/centraloffice.pac';
my $default_url = 'http://www.google.com';
my $default_ip  = '10.25.64.100';

# params
my $pac = param('pac');
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
	if($uri->scheme =~ /http/ or $uri->scheme =~ /ftp/) {
		$url = $uri->as_string;
	} else {
		$url = 'bad';
	}
} else {
	$url = $default_url;
}

if (!$ip) {
	$ip = remote_addr;
	if ($ip eq '127.0.0.1') {
		$ip = '';
	}
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
	}
	h1 {
		font-size: 4em;
		padding-top: 0.5em;
	}
	.result {
		font-family: monospace, serif;
		font-size: 12pt;
		padding-top:    20pt;
		padding-bottom: 80pt;
	}
	input[type="text"] {
		width: 100%;
	}
	p, hr, h1 {
		width: 60%;
		margin-left:  auto;
		margin-right: auto;
		display: block;
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
		p, hr, h1 {
			width: 80%;
		}
		.result {
			padding-top:    20pt;
			padding-bottom: 25pt;
		}
	}
	@media (max-width:520px) {
		h1 {
			font-size: 2em;
			padding-top: 0.3em;
		}
		p, hr, h1 {
			width: 95%;
		}
		.result {
			padding-top:    10pt;
			padding-bottom: 15pt;
		}
	}
/;

# start printing the html doc
print header('text/html'),
	start_html(-title=>'pactester', -style=>{-code=>$css}),
	h1('pactester'),
	start_form(-method=>'GET'),p,
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
		print "Error: Bad PAC $pac",end_html;
		exit 0;
	}
	my $where = $ff->fetch(to=>'/tmp');
	if (!$where) {
		print "Error: Could not fetch PAC $pac",end_html;
		exit 0;
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

	# print summary
	print p,"PAC: ",a({href=>$pac},$pac),br,"URL: ",a({href=>$url},$url),br,"Client IP: $ip";
	if ($exarg) { print br,'Microsoft Extensions enabled.'; }
	print p;
	
	# fork a child process to handle pactester launch
	die "Can't fork: $!" unless defined(my $pid = open(RESULT, '-|'));
	
	if (!$pid) {		# child
	
		# redirect stderr
		open(STDERR, ">&STDOUT");

		# launch pactester
		exec '/usr/bin/pactester',
			'-p', $where,
			'-u', $url,
			$exarg,
			$iparg, $ip
				or die 'exec failed!';
	
		# child is done!
		exit 0;
	
	} else { 		# parent
		
		# read result, add <br> on newline, replace spaces with &nbsp;, etc.
		my $result = '';
		my $sp = ' ';
		my $nbsp = '&nbsp;';
		my $tab = "\t";
		my $nbtab = $nbsp x 4;
		my $da = '-';
		my $nbda = '&#x2011;';
		while (<RESULT>) {
			$_ =~ s/$sp/$nbsp/g;
			$_ =~ s/$tab/$nbtab/g;
			$result .= $_.br;
		}

		# print result
		print p({-class=>'result'}),$result,p,p,hr;
		close RESULT;
	}

	# remove tempfile
	unless (unlink($where)) {
		carp "Warning: Could not delete temp file $where";
	}
}

# about
print p,'This tool uses the pactester&nbsp;utility by Manu&nbsp;Garg (available ',
		a({href=>'https://code.google.com/p/pacparser/'},'here'),').',p;

# parent is done!
print end_html;
exit 0;
