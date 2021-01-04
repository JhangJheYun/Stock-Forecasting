from flask_script import Manager, Server
from main import app

# Setup your app
manager = Manager(app)
# Setup the command to activate server
manager.add_command('runserver', Server())

# Set "python manage.py shell" as activate command of shell
@manager.shell
def make_shell_context():
    return dict(app=app)

if __name__ == '__main__':
    manager.run() 