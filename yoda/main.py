import sys
import click
from pathlib import Path
from storm.parsers.ssh_config_parser import ConfigParser
from plumbum import SshMachine, local

#from plumbum.machines.paramiko_machine import ParamikoMachine
#import paramiko

class Ssh(object):
  def __init__(self, name):
    self.name = name
    self.conn = None
    self.host = None
    self.port = 22
    self.user = "root"
    self.keyfile = str(Path.home()) + "/.ssh/id_rsa"

  def setConfig(self, config):
    self.host = config['hostname']
    if ('port' in config):
      self.port = config['port']
    if ('user' in config):
      self.user = config['user']
    #if ('identityfile' in config):
    #  self.keyfile = config['identityfile']

  def connect(self):
    click.echo("Connecting to host %s" % self.name)
    self.conn = SshMachine(self.host, port = self.port, user = self.user, keyfile = self.keyfile)
    #self.conn = ParamikoMachine(self.host, port = self.port, user = self.user, keyfile = self.keyfile, missing_host_policy=paramiko.AutoAddPolicy())

#pass_ssh = click.make_pass_decorator(Ssh)

@click.group()
@click.option('--host', '-h', default="myserver", help="The name of the connection defined in ~/.ssh/config file")
@click.option('--verbose', '-v', count=True, help="Explain what is being done")
@click.option('--exit/--no-exit', default=False)
@click.pass_context
def yoda(ctx, host, verbose, exit):
  ssh = Ssh(host)
  sshConfigPath = str(Path.home()) + "/.ssh/config"
  config = ConfigParser(sshConfigPath)
  config.load()
  hostConfig = config.search_host(host)
  if (hostConfig == []):
    raise click.ClickException("Host does not exists in %s" % sshConfigPath)
  ssh.setConfig(hostConfig[0]['options'])
  ssh.connect()
  ctx.obj = {
    'ssh': ssh,
    'host': host,
    'exit': exit,
    'verbose': verbose
  }
  if (verbose):
    click.echo("Connected to host %s" % host)

@yoda.command()
@click.argument('path')
@click.pass_context
def mkdir(ctx, path):
  """A basic version of mkdir"""
  cmd = ctx.obj['ssh'].conn['mkdir']
  if (ctx.obj['verbose']):
    click.echo("creating dir %s" % path)
  code, stdout, stderr = cmd['-v', path].run(retcode=None)
  if (code != 0 and ctx.obj['exit']):
    click.echo("Error executing command mkdir: %s" % stderr)
    sys.exit(code)
  return code

@yoda.command()
@click.argument('owner')
@click.argument('file', nargs=-1)
@click.option('--recursive','-R', count=True)
@click.pass_context
def chown(ctx, owner, file, recursive):
  """A basic version of chown command, this is to change the owner of a resource"""
  cmd = ctx.obj['ssh'].conn['chown']
  cmd = cmd['-v']
  if (recursive):
    cmd = cmd['-R']

  for path in file:
    code, stdout, stderr = cmd[owner, path].run(retcode=None)
    if (code != 0):
      click.echo("Error executing command chown: %s" % stderr)
      if (ctx.obj['exit']):
        sys.exit(code)
        break;
    else:
      if (ctx.obj['verbose']):
        click.echo(stdout)
  return code

@yoda.command()
@click.argument('mode')
@click.argument('file', nargs=-1)
@click.option('--recursive','-R', count=True)
@click.pass_context
def chmod(ctx, mode, file, recursive):
  """A basic version of chmod command to change permissions"""
  cmd = ctx.obj['ssh'].conn['chmod']
  cmd = cmd['-v']
  if (recursive):
    cmd = cmd['-R']

  for path in file:
    code, stdout, stderr = cmd[mode, path].run(retcode=None)
    if (code != 0):
      click.echo("Error executing command chmod: %s" % stderr)
      if (ctx.obj['exit']):
        sys.exit(code)
        break;
    else:
      if (ctx.obj['verbose']):
        click.echo(stdout)
  return code

@yoda.command()
@click.argument('remote_user')
@click.option('--keyfilepath','-k', default=None, type=click.Path(exists=True), help="The path to the ssh key file; Default to ~/.ssh/id_rsa.pub")
@click.pass_context
def upload_sshkey(ctx, remote_user, keyfilepath):
  """Upload a ssh key to some user"""
  ssh = ctx.obj['ssh']
  ctx.obj['exit'] = False
  if (not keyfilepath):
    keyfilepath = str(Path.home()) + "/.ssh/id_rsa.pub"
  remoteKeyfileDir = "/home/%s/.ssh/" % remote_user
  remoteKeyfilePath = "/home/%s/.ssh/authorized_keys" % remote_user
  if (ctx.obj['verbose']):
    click.echo('Uploading user key')

  # make dir .ssh
  path = "/home/%s/.ssh" % remote_user
  ctx.invoke(mkdir, path=path)

  keyPath = local.path(keyfilepath)
  if (not keyPath.is_file()):
    click.echo("Key not found in %s"%keyfilepath)
    sys.exit(1)

  F = open(keyfilepath, "r")
  key = F.read()
  code, stdout, stderr = ssh.conn.session().run("echo '%s' >> %s" %(key, remoteKeyfilePath))
  if (code == 0):
    click.echo(stdout)
  else:
    click.echo("Error uploading sshkey: %s" % stderr)
    sys.exit(code)

  # Change permissions
  if (ssh.user != remote_user):
    ctx.invoke(chown, owner=remote_user, file=[remoteKeyfileDir])
    ctx.invoke(chmod, recursive=1, mode='700', file=[remoteKeyfileDir])
    ctx.invoke(chmod, recursive=1, mode='600', file=[remoteKeyfilePath])

  if (ctx.obj['verbose']):
    click.echo("done")





# TODO
# vim /etc/ssh/sshd_config
# edit Port 17000
# edit PermitRootLogin without-password

# service ssh reload
