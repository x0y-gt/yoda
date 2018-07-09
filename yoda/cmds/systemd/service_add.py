import click
from yoda.main import pass_cmd

@click.command('service_add', short_help='Creates a new service in systemd.')
@click.option('-e', '--environment', default="")
@click.argument('service_name')
@click.argument('user')
@click.argument('group')
@click.argument('working_dir')
@click.argument('start_cmd')
@pass_cmd
def cmd(ctx, service_name, user, group, working_dir, start_cmd, environment):
  """Creates a new nginx virtualhost"""
  shell = ctx.shell

  env_path = ""
  if (environment):
    env_path='Environment="PATH=%s"' % environment #/home/sammy/falcon_app/venv/bin

  #install systemctl template
  template = service_template.format(name=service_name, user=user, group=group, working_dir=working_dir, start_cmd=start_cmd, environment=env_path)
  if (ctx.verbose):
    click.echo("Creating service in systemd")
  shell.cmd('echo "" | sudo tee /etc/systemd/system/%s.service' % service_name)
  shell.cmd('sudo chown -v %s:%s /etc/systemd/system/%s.service' % (shell.user, shell.user, service_name))
  file = shell.put(template, '/etc/systemd/system/%s.service' % service_name)
  shell.cmd('sudo chown -v root:root /etc/systemd/system/%s.service' % service_name)

  #reload nginx config
  if (ctx.verbose):
    click.echo("Starting application %s..." % service_name)
  code, output = shell.cmd('sudo systemctl start %s' % service_name)

  #reload nginx config
  if (ctx.verbose):
    click.echo("Enabling application %s in systemd..." % service_name)
  code, output = shell.cmd('sudo systemctl enable %s' % service_name)

  if (ctx.verbose):
    click.echo("%s installed. Done." % service_name)

  return 0

service_template = """
[Unit]
Description={name}
After=network.target

[Service]
User={user}
Group={group}
PIDFile=/tmp/{name}.pid
{environment}
WorkingDirectory={working_dir}
ExecStart="{start_cmd}"
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID

[Install]
WantedBy=multi-user.target
"""
