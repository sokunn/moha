import os

from invoke import task


@task
def workon(ctx):
    if os.environ['ENV'] != 'local':
        return
    if not os.path.exists('~/.virtualenvs/moha'):
        ctx.run('virtualenv ~/.virtualenvs/moha')
    ctx.run('source ~/.virtualenvs/moha/bin/activate')


@task
def theme(ctx):
    ctx.run('curl -LOk https://github.com/divio/django-cms-explorer/archive/master.tar.gz')
    ctx.run('tar -xzf master.tar.gz')
    ctx.run('mv -n django-cms-explorer-master/{*,.*} .')
    ctx.run('rm -rf django-cms-explorer-master/ ./master.tar.gz')


@task
def clean(ctx):
    # cleaning theme files
    ctx.run('rm -rf private/ static/ templates/ tools/ tests/ browserslist gulpfile.js')
    ctx.run('rm -rf .bowerrc .csscomb.json .jscsrc .jshintrc bower.json package.json')
    # cleaning remainings
    ctx.run('rm -rf ~/.virtualenvs/moha/ data/ node_modules/ static/css/')
    # remove pyc files
    ctx.run('find . -name "*.pyc" -delete')


@task
def css(ctx):
    ctx.run('gulp sass')
    ctx.run('gulp watch')


@task(workon)
def runserver(ctx):
    ctx.run('python manage.py runserver')


@task(workon)
def dump(ctx):
    ctx.run('python manage.py dumpdata '
            '-e contenttypes -e admin -e auth.permission --natural --indent=4 > initial_data.json')


@task(workon)
def migrate(ctx):
    ctx.run('python manage.py makemigrations')
    ctx.run('python manage.py migrate --noinput --no-initial-data')


@task
def database(ctx, user='postgres', dbname='moha'):
    res = ctx.run('psql -U {} -tAc "SELECT datname FROM pg_database WHERE datname=\'{}\'"'.format(user, dbname))
    if res.stdout != dbname:
        ctx.run('psql -U {} -c "CREATE DATABASE {};"'.format(user, dbname))


@task
def tests(ctx):
    ctx.run('gulp tests')


@task(workon)
def pulldata(ctx):
    ctx.run('python manage.py migrate --noinput')


@task(pre=[workon], post=[migrate])
def update(ctx):
    ctx.run('pip install -r requirements.txt --no-cache')
    # must check that nodejs, npm, gulp installed globaly!
    # ctx.run('sudo npm install gulp -g')
    ctx.run('npm install')
    ctx.run('gulp sass')


@task(workon, theme, database, update, pulldata)
def install(ctx):
    pass


@task(clean, install)
def reinstall(ctx):
    pass
