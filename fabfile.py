import os
import sys

from fabric.api import *
from fabric import utils

env.public_app = {'name' : 'app_public'}
env.member_app = {'name' : 'app_dashboard'}
env.apps = [env.public_app, env.member_app]

vps = 'ps154456.dreamhost.com'

def _setup_path():
    env.root = env.home
    for app in env.apps:
        app['code_root'] = os.path.join(env.root, app['name'])
    env.virtualenv_root = os.path.join(env.root, 'env')
    env.settings = 'settings_%(environment)s' % env
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
        utils.abort('Create your own dev env; see dev_rfirmin for example')


def dev_navjot():
    env.dev = True
    dev()
    # dir to install virtualenv etc
    env.home = '/home/wb/work/reuben/ssca/'
    env.git_branch = 'develop_navjot1'
    _setup_path()


# feel free to make your own envs
def dev_rf():
    env.dev = True
    dev()
    # dir to install virtualenv etc
    env.home = '/home/rfirmin/code/ssca/'
    _setup_path()


def dev_gc():
    env.dev = True
    dev()
    # dir to install virtualenv etc
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
    for app in env.apps:
        manage(app, 'collectstatic --noinput')
        manage(app, 'syncdb --all')
    update_db('initial', True)
    load_samples()
    touch()

def build():
    update_requirements()
    update_db('auto', False)
    load_samples()

def load_samples():
    for app in env.apps:
        fixture_dirs = ['fixtures']
        if (env.dev):
            fixture_dirs.append('fixtures/dev')

        print ">>>> Loading fixtures for ",app['name']
        fixture_paths = []
        for fixture_dir in fixture_dirs:
            fixture_paths.append(os.path.join(app['code_root'], fixture_dir))

        for fixture_path in fixture_paths:
            fixtures = os.listdir(fixture_path)

            for fixture in fixtures:
                print ">>>>> Loading ",fixture
                manage(app, 'loaddata ' + os.path.join(fixture_path, fixture))
                print "Loaded data from %s" % os.path.join(fixture_path, fixture)

def clean():
    if env.local:
        local('find %(home)s -name \*.pyc -exec rm {} \;' % env)
    else:
        run('find %(home)s -name \*.pyc -exec rm {} \;' % env)

def create_virtualenv():
    require('virtualenv_root', provided_by=('local', 'stag', 'prod'))
    args = '--no-site-packages --clear --distribute'
    if env.local:
        local('rm -fr %(virtualenv_root)s' % env)
        local('virtualenv %s %s' % (args, env.virtualenv_root))
    else:
        run('rm -rf %(virtualenv_root)s' % env)
        run('virtualenv %s %s' % (args, env.virtualenv_root))

def update_requirements():
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
    for app in env.apps:
        with settings(warn_only=True):
            manage(app, 'schemamigration %s --%s' % (app['name'], south))

        if (fake):
            manage(app, 'migrate %s --fake' % app['name'])
        else:
            manage(app, 'migrate %s' % app['name'])


def manage(app, command):
    directory = env.home
    virtualenv(directory, '%(home)smanage.py ' % env + command)

def test():
    manage(env.public_app, 'collectstatic')

def virtualenv(directory, command):
    with cd(directory):
        if (env.local):
            #local(command)
            local(activate() + ' && ' + command)
        else:
            run(activate() + ' && ' + command)


def activate():
    return 'export DEPLOYMENT_ENV="%(environment)s" && . %(virtualenv_root)s/bin/activate' % env


def touch():
    """ touch wsgi file to trigger reload """
    require('home', provided_by=('stag', 'prod'))
    with cd(env.home):
        if env.environment in ['stag', 'prod']:
            run('pkill python')
            run('touch -c passenger_wsgi.py')
