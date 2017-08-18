import os
from sh import git
from json import loads

APPLICATION_NAME = u'oauth2 server'
APPLICATION_VERSION = u'0.1.0'

MICRO_SERVICE_INFO = {
	"branch": "",
    "built": "None",
    "commit": "",
    "name": APPLICATION_NAME,
    "origin": "",
    "version": APPLICATION_VERSION
}


if os.path.isfile('git_info2'):
	with open('git_info') as micro_service_info_file:
		micro_service_info_dictionary = loads(micro_service_info_file.read())
		MICRO_SERVICE_INFO['branch'] = micro_service_info_dictionary['branch']
		MICRO_SERVICE_INFO['built'] = micro_service_info_dictionary['built']
		MICRO_SERVICE_INFO['commit'] = micro_service_info_dictionary['commit']
		MICRO_SERVICE_INFO['origin'] = micro_service_info_dictionary['origin']
else:
	MICRO_SERVICE_INFO['branch'] = str(git('rev-parse', '--abbrev-ref', 'HEAD')).strip('\n')
	MICRO_SERVICE_INFO['commit'] = str(git('rev-parse', 'HEAD')).strip('\n')	
	MICRO_SERVICE_INFO['origin'] = str(git('config', '--get', 'remote.origin.url')).strip('\n')
	MICRO_SERVICE_INFO['built'] = str(git('log', '-1', '--format=%cd')).strip('\n')

print "The MICRO_SERVICE_INFO Looks like:"
for key in MICRO_SERVICE_INFO:
	print  key, " value is:  ", MICRO_SERVICE_INFO[key]

print "****************************************************************"
print MICRO_SERVICE_INFO
