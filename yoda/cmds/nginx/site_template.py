def getSiteTemplate(templateType, siteDomain, ip="", port="80", internal_proxy_port="4000", proxy_port="8000"):
  if (ip):
    address = ip + ":" + port
    proxy_address = ip + ":" + proxy_port
  else:
    address = port
    proxy_address = proxy_port

  return header + templates[templateType].format(domain=siteDomain, address=address, proxy_address=proxy_address, proxy_port=proxy_port, internal_proxy_port=internal_proxy_port)

templates = {
  #php5 ----------------------------------------------------------------------
  'php5': "",

  #php7 ----------------------------------------------------------------------
  'php7': "",

  #html ----------------------------------------------------------------------
  'html': """
server {{
  listen {{address}};

  root /var/www/{domain}/html;

  index index.html index.htm;

  server_name {domain} www.{domain};

  error_log  /var/log/nginx/domains/{domain}.error.log error;
  location / {{
    # First attempt to serve request as file, then as directory, then fall back to displaying a 404.
    try_files $uri $uri/ =404;
    access_log /var/log/nginx/domains/{domain}.log combined;
  }}

  # deny access to .htaccess files, if Apache's document root concurs with nginx's one
  location ~ /\.ht    {{return 404;}}
  location ~ /\.svn/  {{return 404;}}
  location ~ /\.git/  {{return 404;}}
  location ~ /\.hg/   {{return 404;}}
  location ~ /\.bzr/  {{return 404;}}
}}
""",

  #proxy ----------------------------------------------------------------------
  'proxy': """
""",

  #mkdocs ----------------------------------------------------------------------
  'mkdocs': """
server {{
  listen {address};

  index index.html index.htm;

  server_name {domain} www.{domain};

  error_log  /var/log/nginx/domains/{domain}.error.log error;

  location / {{
    proxy_pass http://127.0.0.1:{internal_proxy_port};
    access_log /var/log/nginx/domains/{domain}.log combined;
  }}

  # deny access to .htaccess files, if Apache's document root concurs with nginx's one
  location ~ /\.ht    {{return 404;}}
  location ~ /\.svn/  {{return 404;}}
  location ~ /\.git/  {{return 404;}}
  location ~ /\.hg/   {{return 404;}}
  location ~ /\.bzr/  {{return 404;}}
}}

map $http_upgrade $connection_upgrade {{
  default upgrade;
  '' close;
}}

server {{
  listen {internal_proxy_port};
  server_name {domain} www.{domain};

  location / {{
    proxy_pass http://127.0.0.1:{proxy_port};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }}
}}
"""
}

header = """
##
# You should look at the following URL's in order to grasp a solid
# of Nginx configuration files in order to fully unleash the power of Nginx
# http://wiki.nginx.org/Pitfalls
# http://wiki.nginx.org/QuickStart
# http://wiki.nginx.org/Configuration
#
# Generally, you will want to move this file somewhere, and start with a clean
# file but keep this around for reference. Or just disable in sites-enabled.
#
# Please see /usr/share/doc/nginx-doc/examples/ for more detailed examples.
##

# Note: You should disable gzip for SSL traffic.
# See: https://bugs.debian.org/773332
#
# Read up on ssl_ciphers to ensure a secure configuration.
# See: https://bugs.debian.org/765782
#
# Self signed certs generated by the ssl-cert package
# Don't use them in a production server!
#
# include snippets/snakeoil.conf;

"""
