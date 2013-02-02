import os

from fabric.api import *
from fabric.contrib import files, console
from fabric import utils
from fabric.decorators import hosts

env.project = 'app_public'
vps = 'ps154456.dreamhost.com'

def _setup_path():
    env.root = env.home
    env.code_root = os.path.join(env.root, env.project)
    env.virtualenv_root = os.path.join(env.root, 'env')
    env.settings = '%(project)s.settings_%(environment)s' % env
    env.remote = 'git@bitbucket.org:reubenfirmin/ssca.git'
    print 'using env: %s' % env.environment

def dev():
    """ use dev environment on localhost """
    env.user = 'ssca'
    env.environment = 'dev'
    env.hosts = ['localhost']
    env.home = '~/code/ssca'
    env.git_branch = 'develop'
    # forces local operations. set to false and override hosts if you want to deploy out to a server
    env.local = True
    if not(hasattr(env, 'dev')) or not(env.dev):
        utils.abort('Create your own dev env; see dev_rfirmin for example');

def dev_navjot():
    env.dev = True
    dev()
    # dir to install virtualenv etc
    env.root = '/home/wb/work/reuben/ssca/'
    env.home = '/home/wb/work/reuben/ssca/'
    env.git_branch = 'develop_navjot1'
    _setup_path()

# feel free to make your own envs
def dev_rf():
    env.dev = True
    dev()
    # dir to install virtualenv etc
    env.root = '/home/rfirmin/code/ssca/'
    _setup_path()

def dev_gc():
    env.dev = True
    dev()
    # dir to install virtualenv etc
    env.root = '/home/cetko/projects/ssca/'
    env.home = '/home/cetko/projects/ssca/'
    env.git_branch = 'develop_goran'
    _setup_path()

def stag():
    env.user = 'rfirmin'
    env.environment = 'stag'
    env.hosts = [vps]
    env.home = '/home/rfirmin/sscadev.dreamhosters.com/'
    env.git_branch = 'develop'
    env.local = False
    env.root = '/home/rfirmin/sscadev.dreamhosters.com/'
    _setup_path()

def prod():
    """ use prod environment on remote host"""
    utils.abort('Production deployment not yet implemented.')

def bootstrap():
    """ initialize remote host environment (virtualenv, deploy, update) """
    require('root', provided_by=('dev', 'stag', 'prod'))
    if (env.local):
        local('mkdir -p %(root)s' % env)
    else:
        run('mkdir -p %(root)s' % env)
    create_virtualenv()
    update_requirements()
    manage('collectstatic --noinput')
    manage('syncdb --all')
    update_db('initial', True)
    touch()

def build():
    """ Rebuild. Don't be alarmed if it fails on south, if no models have changed """
    update_requirements()
    update_db('auto', False)

def create_virtualenv():
    """ setup virtualenv on remote host """
    require('virtualenv_root', provided_by=('local', 'stag', 'prod'))
    args = '--no-site-packages --clear --distribute'
    if env.local:
        local('rm -fr %(virtualenv_root)s' % env)
        local('virtualenv %s %s' % (args, env.virtualenv_root))
    else:
        run('rm -rf %(virtualenv_root)s' % env)
        run('virtualenv %s %s' % (args, env.virtualenv_root))

def update_requirements():
    """ update external dependencies on remote host """
    require('code_root', provided_by=('dev', 'stag', 'prod'))
    cmd = ['%(virtualenv_root)s/bin/pip install --upgrade distribute &&' % env]
    cmd += ['%(virtualenv_root)s/bin/pip install' % env]
    #cmd += ['-E %(virtualenv_root)s' % env]
    cmd += ['--requirement %s' % os.path.join(env.root, 'requirements.txt')]
    if (env.local):
        local(' '.join(cmd))
    else:
        run(' '.join(cmd))

def update_db(south, fake):
    """ migrate db using south """
    appname = env.project
    manage('schemamigration %s --%s' % (appname, south))
    if (fake):
        manage('migrate %s --fake' % appname)
    else:
        manage('migrate %s' % appname)

def manage(command):
    require('code_root', provided_by=('dev', 'stag', 'prod'))
    directory = env.code_root
    virtualenv(directory, './manage.py ' + command)

def virtualenv(directory, command):
    with cd(directory):
        if (env.local):
            local(command)
#            local(activate() + ' && ' + command)
        else:
            run(activate() + ' && ' + command)

def activate():
    return 'export DEPLOYMENT_ENV="%(environment)s" && source %(virtualenv_root)s/bin/activate' % env

def touch():
    """ touch wsgi file to trigger reload """
    require('home', provided_by=('stag', 'prod'))
    with cd(env.home):
        if env.environment in ['stag','prod']:
            run('pkill python')
            run('touch -c passenger_wsgi.py')

