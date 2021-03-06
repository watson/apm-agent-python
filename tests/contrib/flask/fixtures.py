import pytest
from flask import Flask, render_template, signals

from elasticapm.contrib.flask import ElasticAPM


@pytest.fixture()
def flask_app():
    app = Flask(__name__)

    @app.route('/an-error/', methods=['GET', 'POST'])
    def an_error():
        raise ValueError('hello world')

    @app.route('/users/', methods=['GET', 'POST'])
    def users():
        return render_template('users.html',
                               users=['Ron', 'Rasmus'])

    return app


@pytest.yield_fixture()
def flask_apm_client(flask_app, test_client):
    client = ElasticAPM(app=flask_app, client=test_client)
    yield client
    signals.request_started.disconnect(client.request_started)
    signals.request_finished.disconnect(client.request_finished)


@pytest.fixture()
def flask_celery(flask_apm_client):
    from celery import Celery

    flask_app = flask_apm_client.app
    celery = Celery(flask_app.import_name, backend=None,
                    broker=None)
    celery.conf.update(CELERY_ALWAYS_EAGER=True)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    celery.flask_apm_client = flask_apm_client
    return celery
