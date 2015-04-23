from subprocess import check_call
from os.path import exists, join
from os import listdir, chdir

from ocdev.plugins.plugin import Plugin
from ocdev.plugins.pluginerror import PluginError

class DevUp(Plugin):

    def __init__(self):
        super().__init__('devup')


    def add_sub_parser(self, main_parser):
        dev_help = """Recursively your core and apps using git pull --rebase.
        Branches are read from your ~/.ocdevrc [devup] section by using the
        following syntax, core is core:
        app = branch
        Only apps listed in there will be considered during update
        """
        parser = main_parser.add_parser('devup', help=dev_help)
        parser.set_defaults(which='devup')
        parser.add_argument('dir', help='Path to core, defaults to the current \
                                         folder', default='', nargs='?')


    def run(self, arguments, directory, settings):
        if arguments.dir != '':
            directory = arguments.dir

        if not exists(join(directory, 'config/config.php')):
            raise PluginError('ownCloud core directory not found in path %s' %directory)

        chdir(directory)

        # update core and 3rdparty
        core_branch = settings.get_value('devup', 'core')
        self.git_pull(core_branch)
        check_call(['git', 'submodule', 'update'])

        # update apps
        for app, branch in settings.get_section('devup').items():
            print('%s %s' %(app, branch))
            if app != 'core':
                app_dir = 'apps/%s' % app
                if exists(app_dir):
                    chdir(app_dir)
                    self.git_pull(branch)
                    chdir('../../')
                else:
                    print('Directory for app %s not found' % app)


    def git_pull(self, branch):
        check_call(['git', 'checkout', branch])
        check_call(['git', 'pull', '--rebase', 'origin', branch])