import click
from yoda.main import pass_cmd

@click.command('site_add', short_help='Initializes a repo.')
@pass_cmd
def cmd(ctx):
  """Creates a new nginx virtualhost"""
  shell = ctx.shell
  shell.verbose = True

  code, output = shell.cmd("sudo ls -l /")
  print(code)
  print(output)

  return 0

siteTemplate = """##
#fastcgi_pass 127.0.0.1:9000;
# With php7.0-fpm:
# fastcgi_pass unix:/run/php/php7.0-fpm.sock;
# of Nginx configuration files in order to fully unleash the power of Nginx.
# http://wiki.nginx.org/Pitfalls
# http://wiki.nginx.org/QuickStart
# http://wiki.nginx.org/Configuration
#
# Generally, you will want to move this file somewhere, and start with a clean
# file but keep this around for reference. Or just disable in sites-enabled.
#
# Please see /usr/share/doc/nginx-doc/examples/ for more detailed examples.
##

server {
  listen 80;
  listen [::]:80;

  root /var/www/domain.com/html/public;

  # Add index.php to the list if you are using PHP
  index index.php index.html index.htm;

                                                                                                                                                                                                                 server_name domain.com www.domain.com;

                                                                                                                                                                                                                         location / {
                                                                                                                                                                                                                         # First attempt to serve request as file, then
                                                                                                                                                                                                                         # as directory, then fall back to displaying a 404.
                                                                                                                                                                                                                         # try_files $uri $uri/ =404;
                                                                                                                                                                                                                         try_files $uri $uri/ /index.php?$query_string;
                                                                                                                                                                                                                         }

                                # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
                                #
                                location ~ \.php$ {
                                include snippets/fastcgi-php.conf;

                                                                                # With php7.0-cgi alone:
                                                                                #fastcgi_pass 127.0.0.1:9000; # With php7.0-fpm: # fastcgi_pass unix:/run/php/php7.0-fpm.sock;
                                                                                # With php5-fpm:
                                                                                fastcgi_pass unix:/run/php/php5.6-fpm.sock;
                                                                                fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
                                                                                }

                                                                                                                                                                                                # deny access to .htaccess files, if Apache's document root
                                                                                                                                                                                                # concurs with nginx's one
                                                                                                                                                                                                location ~ /\.ht/  {return 404;}
                                                                                                                                                                                                location ~ /\.git/  {return 404;}
                                                                                                                                                                                                }"""


