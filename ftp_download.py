import logging, os, ftplib, datetime
from urlparse import urlparse
from flexget.entry import Entry
from flexget.plugin import register_plugin
from flexget.utils.cached_input import cached

log = logging.getLogger('ftp')

class OutputFtp(object):
	"""
		Ftp Download plugin

		input-url: ftp://<user>:<password>@<host>:<port>/<path to file>
		Example: ftp://anonymous:anon@my-ftp-server.com:21/torrent-files-dir

		config:
		    ftp_download:
      			tls: 0 #not used even
	
		TODO:
		  - Resume downloads
		  - use tls
		  - create banlists files
		  - validate conections parameters

	"""
	def validator(self):
		from flexget import validator
        	root = validator.factory('dict')
		#root.accept('list', key='banfiles')
		root.accept('integer', key='tls')
        	return root

	def on_task_download(self, task, config):
		entries = task.accepted
		for entry in entries:
			ftpUrl = urlparse(entry.get('url'))
			title = entry.get('title')
			
			ftp = ftplib.FTP()
			#ftp.set_debuglevel(2)
			ftp.connect(ftpUrl.hostname, ftpUrl.port)
			ftp.login(ftpUrl.username, ftpUrl.password)
			ftp.sendcmd('TYPE I')
			ftp.set_pasv(True)
	
			tmp_path = os.path.join(task.manager.config_base, 'temp', title)
			if not os.path.isdir(tmp_path):
				log.debug('creating tmp_path %s' % tmp_path)
				os.mkdir(tmp_path)

			try: #It's Directory
				ftp.cwd(ftpUrl.path)
				self.ftp_walk(ftp, tmp_path)
			except: #It's File, Downloadit!
				self.ftp_down(ftp, ftpUrl.path, tmp_path)
			
			
	def ftp_walk(self, ftp, tmp_path):
		try: dirs = ftp.nlst(ftp.pwd())
		except: return
    		if not dirs: return
		for item in (path for path in dirs if path not in ('.', '..')):
			try:
				ftp.cwd(item)
				log.info('DIR: %s' % ftp.pwd())
				self.ftp_walk(ftp, tmp_path)
				ftp.cwd('..')
			except Exception, e:
				self.ftp_down(ftp, item, tmp_path)
		

	def ftp_down(self, ftp, fName, tmp_path):
		currdir = os.path.dirname(fName)
		fileName = os.path.basename(fName)
		tmpDir = tmp_path #+ "/" + currdir #os.path.join(tmp_path, currdir)
		if not os.path.exists(tmpDir): os.makedirs(tmpDir)
		try:
			with open(os.path.join(tmpDir,fileName), 'wb') as f:
				def callback(data):
					f.write(data)
				ftp.retrbinary('RETR %s' % fileName, callback)
				f.close()
				log.info('RETR: '+ os.path.join(tmpDir,fileName))
		except Exception, e:
			print e


	def on_task_output(self, task, config):
		entries = task.accepted
		for entry in entries:
			destino = entry.get('path')
			title = entry.get('title')
			origen = os.path.join(task.manager.config_base, 'temp', title)
			log.info('Moviendo a destino: '+destino + ' desde ' + origen);
			import shutil
			shutil.move(origen, destino)

register_plugin(OutputFtp, 'ftp_download', api_ver=2)

