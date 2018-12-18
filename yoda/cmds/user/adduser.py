import click
from pathlib import Path
from yoda.main import pass_cmd

@click.command('adduser', short_help='Creates a new user with random password and selected ssh key.')
@click.option('-k', '--key-path', default="~/.ssh/id_rsa.pub")
@click.argument('user_name')
@pass_cmd
def cmd(ctx, key_path, user_name):
  """Creates a new user"""
  shell = ctx.shell

  home = "/home/%s" % user_name

  #create user for the domain
  if (ctx.verbose):
    click.echo("Creating user...")
  code, output = shell.cmd("sudo adduser --home %s --force-badname --disabled-password %s" % (home, user_name))

  #create .ssh dir
  if (ctx.verbose):
    click.echo("Creating ssh dir...")
  code, output = shell.cmd("sudo mkdir -vp %s/.ssh" % home)

  #upload key
  if (ctx.verbose):
    click.echo("Uploading key")
  shell.cmd('echo "" | sudo tee %s/.ssh/authorized_keys' % home)
  key_path = key_path.replace('~', str(Path.home()))
  with open(key_path) as file:
    key = file.read()
    file = shell.put(key, "%s/.ssh/authorized_keys" % home)
  #code, output = shell.cmd('printf "%s" | sudo tee /etc/nginx/sites-available/%s' % (template, site_domain))
  shell.cmd('sudo chmod -v 600 %s/.ssh/authorized_keys' % home)
  shell.cmd('sudo chmod -v 700 %s/.ssh' % home)
  shell.cmd('sudo chown -Rv %s:%s %s/.ssh' % (user_name, user_name, home))

  #enable sudo
  if (ctx.verbose):
    click.echo("Adding to SUDO group...")
  code, output = shell.cmd("sudo usermod -aG sudo %s" % user_name)

  if (ctx.verbose):
    click.echo("%s added. Done." % user_name)

  return 0
