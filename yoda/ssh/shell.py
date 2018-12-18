import sys
import paramiko
import getpass
import tempfile
from pathlib import Path
from time import sleep

class Shell(object):
  WAIT_FOR_DATA = 0.1 #seconds
  # Max buffer in a paramiko shell
  BUFFER_SIZE = 1000 #32767
  # To stop receiving data
  SHELL_CHARACTER = ["$ ", "# "]
  INPUT_CHARACTERS = [": ", "[Y/n] ", "[y/N] ", "[y/n] "]
  EXIT_CODE = 'EXIT_CODE:'
  TAIL_LENGTH = 100

  def __init__(self, name):
    self.name = name
    self.shell = None
    self.sftp = None
    self.host = None
    self.port = 22
    self.user = "root"
    self.keyfile = str(Path.home()) + "/.ssh/id_rsa"
    self.force = False
    self.interactive = False
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
    client.connect(self.host, port=self.port, username=self.user, key_filename=self.keyfile, timeout=30)
    self.shell = client.invoke_shell()
    self.sftp = client.open_sftp()
    sleep(Shell.WAIT_FOR_DATA)
    #Receive the data output
    self.recv()
    self.shellStopCharacters = [Shell.EXIT_CODE] + Shell.SHELL_CHARACTER + Shell.INPUT_CHARACTERS

  # Execute remote cmd
  def cmd(self, cmd, input=False):
    self._cmdCurrent = cmd
    self._cmdExecuting = True
    rmtCmd = self._remoteCmd(cmd) + '\n'
    sent = self.shell.sendall(rmtCmd)
    if (self.interactive):
      print("%s$> %s" % (self.name, cmd))
    output = ''
    while self._cmdExecuting:
      code, buffer = self.recv()
      output += buffer

    #exit if code is different than 0
    if (code != 0):
      sys.exit(code)

    return [code, output]

  def recv(self):
    buffer = self.shell.recv(Shell.BUFFER_SIZE).decode("utf-8")
    buffer = self._cleanBuffer(buffer)
    tail = buffer[-Shell.TAIL_LENGTH:]
    sleep(Shell.WAIT_FOR_DATA)
    while not any(stopWord in tail for stopWord in self.shellStopCharacters):
      buffer += self.shell.recv(Shell.BUFFER_SIZE).decode("utf-8")
      buffer = self._cleanBuffer(buffer)
      #print(temp, end='', flush=True)

      tail = buffer[-Shell.TAIL_LENGTH:]
      sleep(Shell.WAIT_FOR_DATA)

    # Verify if it stops asking for input
    if self._cmdExecuting and tail.endswith(tuple(Shell.INPUT_CHARACTERS)):
      #print if interactive
      if (self.interactive):
        print(buffer) #, end='', flush=True)

      # Get the last line - not efficient
      # Missing support for: Is the information correct? [Y/n]
      lastLine = buffer.splitlines()[-1]
      if ('password' in lastLine.lower()):
        stdin = getpass.getpass('[local] Password: ')
      else:
        stdin = input('[local]: ')
      self.shell.send(stdin + '\n')
      return None, buffer

    if Shell.EXIT_CODE in tail:
      self._cmdExecuting = False
      buffer, code = buffer.split(Shell.EXIT_CODE)
      if(not code.isdigit()):
        code = code[:code.find('\r\n')]
      code = int(code)

      #print if interactive and if buffer is not empty
      buffer = buffer.strip()
      if (self.interactive and buffer):
        print(buffer) #, end='', flush=True)

      return [code, buffer]

    return None, buffer

  def put(self, content, path):
    fileStats = None
    with tempfile.NamedTemporaryFile(mode='w+') as fp:
      fp.write(content)
      fp.flush()

      fileStats = self.sftp.put(fp.name, path)

    return fileStats

  def _cleanBuffer(self, buffer):
    # Remove some stuff from buffer
    if (self._cmdExecuting and " \r" in buffer):
      buffer = buffer.replace(" \r", '') # Some trash because of the emulations of the shell
    if (self._cmdExecuting and self._remoteCmd(self._cmdCurrent) in buffer):
      buffer = buffer.replace(self._remoteCmd(self._cmdCurrent), '') # remove current cmd
    return buffer

  def _remoteCmd(self, cmd):
    return cmd + ' ; echo "%s$?"' % Shell.EXIT_CODE
