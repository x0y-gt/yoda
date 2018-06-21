import click
from yoda.main import pass_cmd
from yoda.cmds.nginx.site_template import getSiteTemplate

@click.command('site_add', short_help='Creates a new nginx virtualhost.')
@click.option('-t', '--site-type', default="html", type=click.Choice(['html', 'php5', 'php7', 'node', 'mkdocs']))
@click.argument('site_domain')
@pass_cmd
def cmd(ctx, site_type, site_domain):
  """Creates a new nginx virtualhost"""
  shell = ctx.shell

  #create user for the domain
  if (ctx.verbose):
    click.echo("Creating user")
  home = "/var/www/%s" % site_domain
  #code, output = shell.cmd("sudo useradd -d %s -U %s" % (home, site_domain))

  #change password
  if (ctx.verbose):
    click.echo("Changing user password")
  #code, output = shell.cmd("sudo passwd %s" % site_domain)

  #Create site dir
  if (ctx.verbose):
    click.echo("Creating site directory")
  #code, output = shell.cmd("sudo mkdir -vp /var/www/%s/html" % site_domain)

  #Change permissions

  #Create directory for logs if not exists
  if (ctx.verbose):
    click.echo("Creating directory for site logs")
  #code, output = shell.cmd('sudo mkdir -vp /var/log/nginx/domains')

  #install site template
  template = getSiteTemplate(site_type, site_domain)
  template = repr(template)
  template = template.split("\\n")
  template = "\\n".join(template[1:-1])
  template = template.replace('!','')
  template = template.replace('"','\\"')
  template = template.replace("$","\$")
  # $ character
  if (ctx.verbose):
    click.echo("Creating server block in nginx")
  code, output = shell.cmd('printf "%s" | sudo tee /etc/nginx/sites-available/%s' % (template, site_domain))

  #Install mkdocs?

  #Create symbolic link to sites-enabled
  if (ctx.verbose):
    click.echo("Creating symbolic link to sites-enabled")
  #code, output = shell.cmd('sudo ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/' % site_domain)

  #reload nginx config
  if (ctx.verbose):
    click.echo("Restarting nginx")
  #code, output = shell.cmd('sudo systemctl restart nginx')

  if (ctx.verbose):
    click.echo("%s installed. Done." % site_domain)

  return 0
