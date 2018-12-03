import os
from cloudfoundry_client.client import CloudFoundryClient
import json


class PCFClass:

    def __init__(self):
        self.__spaces = []
        self.__apps = []
        self.__scaler_conf = {}
        api_endpoint = os.getenv("api_endpoint")
        username = os.getenv("user")
        password = os.getenv("password")
        proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))
        print("Connecting to Api:{}".format(api_endpoint))
        self.__client = CloudFoundryClient(api_endpoint, proxy=proxy, verify=False)
        print("Authenticating")
        self.__client.init_with_user_credentials(username, password)
        print("Initializing PCF spaces")
        self.get_spaces()
        print("Initializing PCF apps")
        self.get_apps()
        self.init_scaling_confs()

    def get_apps(self):
        self.__apps.clear()
        for item in self.__client.v2.apps:
            self.__apps.append(item["entity"])
        return self.__apps

    def get_spaces(self):
        self.__spaces.clear()
        for item in self.__client.v2.spaces:
            self.__spaces.append(item["entity"])
        return self.__spaces

    def get_space(self, space_name):
        for item in self.__spaces:
            if item["name"] == space_name:
                return item

    def get_space_guid(self, space_name):
        for space in self.__spaces:
            if space_name == space["name"]:
                return space["apps_url"].split("/")[3]

    def get_app_guid(self, space_name, app_name):
        space_guid = self.get_space_guid(space_name)
        for app in self.__apps:
            if app_name == app["name"] and app["space_guid"] == space_guid:
                return app["service_bindings_url"].split("/")[3]

    def get_org_guid(self, org_name):
        org = self.get_org(org_name)[0]
        return org["spaces_url"].split("/")[-2]

    def get_org(self, org_name):
        org_list = []
        query = {}
        if org_name is not None:
            query["name"] = org_name
        for org in self.__client.v2.organizations.list(**query):
            org_list.append(org["entity"])
        return org_list

    def apps(self, space_name=None, app_name=None):
        space_guid = None
        app_list = []
        if space_name:
            space_guid = self.get_space_guid(space_name)
        for item in self.__apps:
            if not app_name or item["name"] == app_name:
                if not space_name or item["space_guid"] == space_guid:
                    app_list.append(item)
        return app_list

    def services(self):
        service_list = []
        for item in self.__client.v2.services:
            service_list.append(item)
        return service_list

    def service_keys(self):
        service_keys = []
        for item in self.__client.v2.service_keys:
            service_keys.append(item)
        return service_keys

    def get_buildpack(self, space_name, app_name):
        app_summary = self.app_summary(app_name,space_name)
        buildpack = {
            "name":  app_summary["buildpack"],
            "buildpack_guid": app_summary["detected_buildpack_guid"],
            "type": app_summary["detected_buildpack"]
        }
        return buildpack

    def get_buildpacks(self):
        buildpacks = []
        for item in self.__client.v2.buildpacks:
            buildpacks.append(item["entity"])
        return buildpacks

    def space_service_instances(self, space_name, service_name):
        service_instances = []
        space_guid = self.get_space_guid(space_name)
        query = {
            'space_guid': space_guid
        }
        if service_name is not None:
            query['name'] = service_name
        for item in self.__client.v2.service_instances.list(**query):
            service_instances.append(item['entity'])
        return service_instances

    def app_service_bindings(self, space_name, app_name, service_name):
        service_bindings = []
        service_guid = self.get_service_guid(space_name, app_name, service_name)
        app_guid = self.get_app_guid(space_name, app_name)
        query = {
            'app_guid': app_guid
        }
        if service_guid is not None:
            query['service_instance_guid'] = service_guid
        for item in self.__client.v2.service_bindings.list(**query):
            service_bindings.append(item["entity"])
        return service_bindings

    def remove_app_service_binding(self, space_name, app_name, service_name):
        service_guid = self.get_service_binding_id(space_name, app_name, service_name)
        self.__client.v2.service_bindings.remove(service_guid)

    def remove_space_service_instances(self, space_name, service_name):
        print("service name {}".format(service_name))
        service_guid = self.space_service_instances(space_name, service_name)[0]['service_bindings_url'].split("/")[-2]
        print("Received service guid {}".format(service_guid))
        self.__client.v2.service_instances.remove(service_guid)

    def get_service_guid(self, space_name, app_name, service_name):
        app_summary = self.app_summary(app_name, space_name)
        for service in app_summary["services"]:
            if service_name == service["name"]:
                return service["guid"]

    def get_service_binding_id(self, space_name, app_name, service_name):
        service_guid = self.get_service_guid(space_name, app_name, service_name)
        app_guid = self.get_app_guid(space_name, app_name)
        query = {
            'app_guid': app_guid,
            'service_instance_guid': service_guid
        }
        for item in self.__client.v2.service_bindings.list(**query):
            return item["entity"]["service_binding_parameters_url"].split("/")[-2]

    def app_stats(self, app_name, space_name):
        space_guid = self.get_space_guid(space_name)
        for item in self.__client.v2.apps.list(**{'name': app_name, 'space_guid': space_guid}):
            return item.stats()

    def app_summary(self, app_name, space_name):
        space_guid = self.get_space_guid(space_name)
        for item in self.__client.v2.apps.list(**{'name': app_name, 'space_guid': space_guid}):
            return item.summary()

    def get_url(self, url):
        return self.__client.get(url)

    def init_scaling_confs(self):
        for space in self.__spaces:
            scale_service_binding = self.space_service_instances(space["name"], "autoscale")
            if len(scale_service_binding) != 0:
                dashboard_url = (scale_service_binding[0]["dashboard_url"]) \
                                .replace("dashboard", "api") + "/bindings"
                try:
                    response = self.get_url(dashboard_url)
                    self.__scaler_conf[space["name"]] = json.loads(response.content)["resources"]
                except Exception as err:
                    self.__scaler_conf[space["name"]] = None
                    print('Exception occurred auto scale service url:', err)

    def get_scaling_conf(self, space_name, app_name):
        if space_name not in self.__scaler_conf:
            return {"max_instances": 0, "enabled": "false"}
        else:
            for item in self.__scaler_conf[space_name] or []:
                if item["app_name"] == app_name:
                    return item
            return {"max_instances": 0, "enabled": "false"}

