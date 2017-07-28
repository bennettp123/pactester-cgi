# [pactester-cgi](https://github.com/bennettp123/pactester-cgi)

CGI frontend to pactester: https://github.com/pacparser/pacparser

Requires perl and pactester.


### Quickstart

Launch the docker image:

```
docker run --rm -it -p 80:80 bennettp123/pactester-web:latest
```

The server will run on port 80.


### Manual installation

1. Copy pactester.cgi to /usr/lib/cgi-bin/pactester/pactester.cgi
2. Add the following to httpd.conf:

```ApacheConf
ScriptAlias /pactest.html /usr/lib/cgi-bin/pactester/pactester.cgi
<Directory /usr/lib/cgi-bin/pactester>
  Options ExecCGI
  AllowOverride None
  Order allow,deny
  Allow from all
</Directory>
```


### Why?

Troubleshooting pac files, duh. :)
