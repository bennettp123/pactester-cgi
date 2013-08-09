# pactester-cgi

Frontend to pactester: https://code.google.com/p/pacparser/

# installation

1. Copy pactester.cgi to /usr/lib/cgi-bin/pactester/pactester.cgi
2. Add the following to httpd.conf:

  ScriptAlias /pactest.html /usr/lib/cgi-bin/pactester/pactester.cgi
  <Directory /usr/lib/cgi-bin/pactester>
    Options ExecCGI
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>
