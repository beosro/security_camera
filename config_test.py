import ConfigParser

config = ConfigParser.ConfigParser()
config.read('params.cfg')

print config.get('general', 'location')

