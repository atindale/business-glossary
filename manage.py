"""
This is the main manage.py script.

From here you can load and dump data and start the built-in webserver.

Copyright 2016, 2017 Alan Tindale
"""

import os
import datetime

COV = None

if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app.extensions import db

from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from app.core import create_app

from app.config import BASE_DIR

# Create application from BG_CONFIG environment variable or use default.
app = create_app(os.getenv('BG_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def clear_db():
    '''Clear the database'''
    db.drop_all()
    db.create_all()


@manager.command
def load_data(filename):
    '''Load data into application'''
    from app.loader import load_yaml
    load_yaml.load(filename)


@manager.option('-y', '--yaml', help='Dump to yaml format', dest='yaml', default=False, action="store_true")
@manager.option('-j', '--json', help='Dump to json format', dest='json', default=False, action="store_true")
@manager.option('-d', '--dir', help='Specify a directory where the export file will be created', dest='dir', default='None')
def dump(yaml, json, dir):
    '''Dump data from application'''

    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")

    if dir == "None":
        file_path = os.path.join(os.path.dirname(BASE_DIR), 'bg_interface')
    else:
        file_path = dir

    if not os.path.isdir(file_path):
        print("The directory %s does not exist" % file_path)
        return

    file_name = os.path.join(file_path, "bg_export_" + timestr)

    if yaml:
        from app.loader import dump_yaml
        dump_yaml.dump(file_name + ".yaml")

    if json:
        from app.loader import dump_json
        dump_json.dump(file_name + ".json")


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        covdir = os.path.join(BASE_DIR, 'htmlcov')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)

if __name__ == '__main__':
    manager.run()
