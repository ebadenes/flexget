import logging
from flexget import validator
from flexget.plugin import register_plugin, PluginWarning
from flexget.plugins.filter.series import forget_series_episode

log = logging.getLogger('forget')

class OutputForget(object):
	def validator(self):
		return validator.factory('boolean')

	def on_task_output(self, task, config):
		for entry in task.accepted:
			try:
				forget_series_episode(entry['series_name'], entry['series_id'])
				log.info('Removed episode `%s` from series `%s`.' % (entry['series_id'], entry['series_name']))
			except ValueError:
    				log.info("Series (%s) or id (%s) unknown." % (entry['series_name'],entry['series_id']))

register_plugin(OutputForget, 'forget', api_ver=2)

