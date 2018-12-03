from classes.pcf_client import PCFClass
from classes.app_stats import APPMetrics
from apscheduler.schedulers.background import BackgroundScheduler
from flask_httpauth import HTTPTokenAuth
from flask import Flask, g, request
import json


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Token')
tokens = {
    "DevOps123": "DevOps"
}


@auth.verify_token
def verify_token(token):
    if token in tokens:
        g.current_user = tokens[token]
        return True
    return False


class Clients:
    pcf_client = PCFClass()
    metrics = APPMetrics(pcf_client)


def schedule_client_creation():
    Clients.pcf_client = PCFClass()
    Clients.metrics = APPMetrics(Clients.pcf_client)


def schedule_getting_scaler_confs():
    Clients.pcf_client.init_scaling_confs()


cron = BackgroundScheduler(daemon=True)
cron.add_job(schedule_client_creation, 'interval', weeks=1)
cron.add_job(schedule_getting_scaler_confs, 'interval', minutes=5)
cron.start()


@app.route("/")
def welcome():
    return json.dumps("Pivotal Cloud Foundry API by DevOps")


@app.route("/spaces/<string:space_name>")
def space(space_name):
    return json.dumps(Clients.pcf_client.get_space(space_name))


@app.route("/spaces")
@app.route("/spaces/")
def spaces():
    return json.dumps(Clients.pcf_client.get_spaces())


@app.route("/apps")
@app.route("/apps/")
@auth.login_required
def get_apps():
    return json.dumps(Clients.pcf_client.get_apps())


@app.route("/services")
@auth.login_required
def services():
    return json.dumps(Clients.pcf_client.services())


@app.route("/spaces/<string:space_name>/apps/<string:app_name>/buildpack")
@app.route("/spaces/<string:space_name>/apps/<string:app_name>/buildpack/")
def get_buildpack(space_name, app_name):
    return json.dumps(Clients.pcf_client.get_buildpack(space_name, app_name))


@app.route("/buildpacks")
def get_buildpacks():
    return json.dumps(Clients.pcf_client.get_buildpacks())


@app.route("/spaces/<string:space_name>/service_instances")
@app.route("/spaces/<string:space_name>/service_instances/<string:service_name>")
@auth.login_required
def space_service_instances(space_name, service_name=None):
    return json.dumps(Clients.pcf_client.space_service_instances(space_name, service_name))


@app.route("/service_keys")
@auth.login_required
def service_keys():
    return json.dumps(Clients.pcf_client.service_keys())


@app.route("/spaces/<string:space_name>/apps/<string:app_name>/service_bindings")
@app.route("/spaces/<string:space_name>/apps/<string:app_name>/service_bindings/<string:service_name>")
@auth.login_required
def app_service_bindings(space_name, app_name, service_name=None):
    return json.dumps(Clients.pcf_client.app_service_bindings(space_name, app_name, service_name))


@app.route("/spaces/<string:space_name>/apps/<string:app_name>/service_bindings/<string:service_name>", methods=['DELETE'])
@auth.login_required
def remove_app_service_binding(space_name, app_name, service_name):
    return json.dumps(Clients.pcf_client.remove_app_service_binding(space_name, app_name, service_name))


@app.route("/spaces/<string:space_name>/service_bindings/<string:service_name>", methods=['DELETE'])
@auth.login_required
def remove_space_service_binding(space_name, service_name):
    return json.dumps(Clients.pcf_client.remove_space_service_binding(space_name, service_name))


@app.route("/spaces/<string:space_name>/apps")
@app.route("/spaces/<string:space_name>/apps/<string:app_name>")
@auth.login_required
def apps(space_name=None, app_name=None):
    return json.dumps(Clients.pcf_client.apps(space_name, app_name))


@app.route("/spaces/<string:space_name>/apps/<string:app_name>/stats")
def app_stats(app_name, space_name):
    return json.dumps(Clients.pcf_client.app_stats(app_name, space_name))


@app.route("/spaces/<string:space_name>/apps/<string:app_name>/summary")
@auth.login_required
def app_summary(space_name=None, app_name=None):
    return json.dumps(Clients.pcf_client.app_summary(app_name, space_name))


@app.route("/spaces/<string:space_name>/apps/<string:app_name>/metrics")
def app_metrics(app_name, space_name):
    return json.dumps(Clients.metrics.get_app_metrics(app_name, space_name))


@app.route("/metrics_urls/<string:org_name>")
def get_metrics_urls(org_name):
    return json.dumps(Clients.metrics.get_metrics_urls(org_name))


@app.route("/organizations")
@app.route("/organizations/<string:org_name>")
def get_organizations(org_name=None):
    return json.dumps(Clients.pcf_client.get_org(org_name))


#@app.before_request
#def log_request_info():
#    app.logger.debug('Headers: %s', request.headers)
#    app.logger.debug('Body: %s', request.get_data())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
