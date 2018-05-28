from storm.parsers.ssh_config_parser import ConfigParser
from pathlib import Path

def importHost(host):
  sshConfigPath = str(Path.home()) + "/.ssh/config"
  config = ConfigParser(sshConfigPath)
  config.load()
  hostConfig = config.search_host(host)
  if (hostConfig == []):
    raise Exception("Host does not exists in %s" % sshConfigPath)
  return hostConfig
