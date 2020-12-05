import tripadvisor
import flask_script as script
from flask_migrate import Migrate, MigrateCommand
from prometheus_flask_exporter.multiprocess import UWsgiPrometheusMetrics
from tripadvisor.models import User, Follow, TripAdvisor, Comment,\
                             Love, Child_cmt, Click, Comment_like


app = tripadvisor.create_application()
migrate = Migrate(app, tripadvisor.db)
manager = script.Manager(app)
manager.add_command('runserver', script.Server(host='0.0.0.0', port=8000))
manager.add_command('shell', script.Shell(make_context=lambda: {
    'current_app': app
}))

try:
    metrics = UWsgiPrometheusMetrics(app=app, default_labels={'project': 'hotel'})
    metrics.start_http_server(9200)
except ModuleNotFoundError:
    pass


def make_shell_context():
    return dict(app=app, db=tripadvisor.db, User=User, Follow=Follow, Food=Food, Survey=Survey, TripAdvisor=TripAdvisor)

manager.add_command('db', MigrateCommand)

if __name__=="__main__":
    manager.run()
