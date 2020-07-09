import os
import tripadvisor
from tripadvisor.models import User, Role, Post, Follow, Survey, TripAdvisor, Hotel, Comment,Love, Child_cmt, Click,Comment_like
import flask_script as script
from flask_migrate import Migrate, MigrateCommand

app = tripadvisor.create_application()
manager = script.Manager(app)
migrate = Migrate(app, tripadvisor.db)
manager.add_command('runserver', script.Server(host='0.0.0.0', port=8000))
manager.add_command('shell', script.Shell(make_context=lambda: {
    'current_app': app
}))


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Follow=Follow, Food=Food,Survey=Survey, TripAdvisor=TripAdvisor)

manager.add_command('db',MigrateCommand)

if __name__=="__main__":
    manager.run()
