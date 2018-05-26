import paramiko
import getpass
from pathlib import Path
from time import sleep

import sys

class Shell(object):
  WAIT_FOR_DATA = 0.1 #seconds
  # Max buffer in a paramiko shellel
  BUFFER_SIZE = 32768
  # To stop receiving data
  SHELL_CHARACTER = ["$ "]
  INPUT_CHARACTERS = [": "]
  EXIT_CODE = 'EXIT_CODE:'
  TAIL_LENGTH = 100

  def __init__(self, name):
    self.name = name
    self.shell = None
    self.host = None
    self.port = 22
    self.user = "root"
    self.keyfile = str(Path.home()) + "/.ssh/id_rsa"
    self.verbose = False
    self.shellStopCharacters = Shell.SHELL_CHARACTER #Just at the beginning
    self._cmdCurrent = ''
    self._cmdExecuting = False

  def setConfig(self, config):
    self.host = config['hostname']
    if ('port' in config):
      self.port = config['port']
    if ('user' in config):
      self.user = config['user']
    if ('identityfile' in config):
      self.keyfile = config['identityfile'][0]
      if ("~" in self.keyfile):
        self.keyfile = self.keyfile.replace('~', str(Path.home()))

  def connect(self):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(self.host, port=self.port, username=self.user, key_filename=self.keyfile)
    self.shell = client.invoke_shell()
    sleep(Shell.WAIT_FOR_DATA)
    code, stdout = self.recv()
    if (self.verbose):
      print(stdout)
    self.shellStopCharacters = [Shell.EXIT_CODE] + Shell.SHELL_CHARACTER + Shell.INPUT_CHARACTERS

  def cmd(self, cmd, input=False):
    self._cmdCurrent = cmd
    self._cmdExecuting = True
    self.shell.send(self._remoteCmd(cmd) + '\n')
    return self.recv()

  def recv(self):
    buffer = self.shell.recv(Shell.BUFFER_SIZE).decode("utf-8")
    tail = buffer[-Shell.TAIL_LENGTH:]
    while not any(stopWord in tail for stopWord in self.shellStopCharacters):
      buffer += self.shell.recv(Shell.BUFFER_SIZE).decode("utf-8")
      tail = buffer[-Shell.TAIL_LENGTH:]
      sleep(Shell.WAIT_FOR_DATA)

    # Remove some lines from output
    if (self._cmdExecuting):
      _blackHole, buffer = buffer.split(self._remoteCmd(self._cmdCurrent)) # remove current cmd

    # Verify if it stops asking for input
    if any(stopWord in tail for stopWord in Shell.INPUT_CHARACTERS):
      pass
      # Ask for input

    if Shell.EXIT_CODE in tail:
      self._cmdExecuting = False
      buffer, code = buffer.split(Shell.EXIT_CODE)
      code = code[:code.find('\r\n')]
      return [code, buffer]
    return None, buffer

  def _remoteCmd(self, cmd):
    return cmd + ' ; echo "%s$?"' % Shell.EXIT_CODE
