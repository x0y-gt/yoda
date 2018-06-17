import os
import click
from yoda.ssh.shell import Shell
from yoda.ssh.config import importHost

# Context obj
class Cmd():
  def __init__(self):
    self.verbose = False
    self.shell = None
    self.host = None

pass_cmd = click.make_pass_decorator(Cmd, ensure=True)

class CmdsLoader(click.MultiCommand):
  _cmdFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cmds'))

  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(self._cmdFolder):
      if filename.endswith('.py'):
        rv.append(filename[:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      cmdFullName = 'yoda.cmds.' + name
      mod = __import__(cmdFullName, None, None, ['cmd'])
    except ImportError:
      return
    return mod.cmd

@click.command(cls=CmdsLoader)
@click.option('-v', '--verbose', count=True, help="Explain what is being done")
@click.option('-i', '--interactive', count=True, help="Show all the output from the established remote shell session")
@click.option('-h', '--host', default="myserver", help="The name of the connection defined in ~/.ssh/config file")
@click.pass_context
def yoda(ctx, verbose, interactive, host):
  shell = Shell(host)
  hostConfig = importHost(host)
  shell.setConfig(hostConfig[0]['options'])
  shell.connect()
  if (verbose):
    click.echo("Connected to host %s" % host)

  # Setting up cmd context
  shell.interactive = bool(interactive)
  cmd = Cmd()
  cmd.shell = shell
  cmd.host = host
  cmd.verbose = verbose

  ctx.obj = cmd



# TODO
# vim /etc/ssh/sshd_config
# edit Port 17000
# edit PermitRootLogin without-password

# service ssh reload
