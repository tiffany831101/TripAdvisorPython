import os
from app import create_app, db
from app.models import User, Role, Post, Follow, Survey, TripAdvisor, Hotel, Comment,Love, Child_cmt, Click,Comment_like
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Follow=Follow, Food=Food,Survey=Survey, TripAdvisor=TripAdvisor)

manager.add_command('db',MigrateCommand)

if __name__=="__main__":
    manager.run()


