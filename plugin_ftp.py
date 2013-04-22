import logging, os, ftplib, datetime
from urlparse import urlparse
from flexget.entry import Entry
from flexget.plugin import register_plugin
from flexget.utils.cached_input import cached

log = logging.getLogger('ftp')

class InputFtp(object):
	def validator(self):
		from flexget import validator
        	root = validator.factory('dict')
        	root.accept('list', key='dirs').accept('text')
		config = root.accept('dict', key='config', required=True)
		config.accept('integer', key='use-ssl')
		config.accept('text', key='name')
		config.accept('text', key='username')
		config.accept('text', key='password')
		config.accept('text', key='host')
		config.accept('integer', key='port')

        	return root

	def on_task_input(self, task, config):
		if(config['config']['use-ssl'] == 1):
			ftp = ftplib.FTP_TLS()
		else:
			ftp = ftplib.FTP()

		#ftp.set_debuglevel(2)
		ftp.connect(config['config']['host'], config['config']['port'])
		ftp.login(config['config']['username'], config['config']['password'])
		ftp.sendcmd('TYPE I')
		ftp.set_pasv(True)
		entries = []
		for path in config['dirs']:
			baseurl = "ftp://%s:%s@%s:%s/" % (config['config']['username'], config['config']['password'], config['config']['host'], config['config']['port'] ) 
			dirs = ftp.nlst(path)
			for p in dirs:
				url = baseurl + p
				title = os.path.basename(p)
				#title = title.replace('.', ' ')
				entry = Entry()
				entry['title'] = title
				entry['description'] = title
				entry['url'] = url
				entries.append(entry)
		return entries

register_plugin(InputFtp, 'ftp_list', api_ver=2)
