from flask import Flask
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager,Server
from app import create_app,db

app = create_app()
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('runserver',Server(use_debugger=True,host='127.0.0.1',port=9999))
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()
