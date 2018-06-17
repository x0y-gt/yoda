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

  if (ctx.verbose):
    click.echo("Creating directory for site logs")
  code, output = shell.cmd("sudo mkdir -vp /var/log/nginx/domains")

  #template = getSiteTemplate(site_type, site_domain)
  #print(template)

  print(int(code))
  #print(output)

  return 0
