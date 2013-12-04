from os import path
import os
import sublime
import sublime_plugin


YO_CMD = 'yo'
DEBUG = True


class TamiaCommand(sublime_plugin.WindowCommand):
	def run(self, *args, **kwarg):
		self.generator = kwarg.get('generator', False)
		if not self.generator:
			sublime.status_message('Generator not defined.')
			return

		self.root_dir = self.project_root()
		if not self.root_dir:
			sublime.status_message('Gruntfile not found.')
			return

		self.settings = sublime.load_settings('Tamia.sublime-settings')

		prompt = kwarg.get('prompt', 'Enter name:')
		self.show_prompt(prompt)

	def on_prompt_done(self, name):
		# Extra environments variables
		env = os.environ.copy()
		extra_env = self.settings.get('env', {})
		env.update(extra_env)

		# Extra path
		extra_path = self.settings.get('path')
		if extra_path:
			env['PATH'] = ':'.join([extra_path, env['PATH']])

		exec_args = {
			'cmd': '%s tamia:%s %s' % (YO_CMD, self.generator, name),
			'shell': True,
			'working_dir': self.root_dir,
			'env': env
		}
		if not DEBUG: exec_args['quiet'] = True

		sublime.status_message('Starting Yo...')
		self.window.run_command('exec', exec_args)
		if not DEBUG: self.window.run_command('hide_panel', {'panel': 'output.exec'})

	def project_root(self):
		dir = self.window.active_view().file_name()
		while True:
			parent = path.realpath(path.join(dir, '..'))
			if parent == dir:  # System root folder
				break
			dir = parent
			has = lambda f: path.isfile(path.join(dir, f))
			if has('Gruntfile.js') or has('Gruntfile.coffee'):
				return dir
		return None

	def show_prompt(self, prompt=''):
		self.input_panel_view = self.window.show_input_panel(
			prompt, '',
			self.on_prompt_done, None, None
		)

		self.input_panel_view.set_name('TamiaPrompt')
		self.input_panel_view.settings().set("auto_complete_commit_on_tab", False)
		self.input_panel_view.settings().set("tab_completion", False)
		self.input_panel_view.settings().set("translate_tabs_to_spaces", False)
		self.input_panel_view.settings().set("anf_panel", True)
