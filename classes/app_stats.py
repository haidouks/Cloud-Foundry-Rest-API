import os
import json


class APPMetrics:

    def __init__(self, pcf_client):
        self.__pcf = pcf_client

    def get_app_metrics(self, app_name, space_name):
        self.__app_summary = self.__pcf.app_summary(app_name, space_name)

        app_metrics = {}
        if self.__app_summary["state"] == "STARTED":
            self.__app_stats = self.__pcf.app_stats(app_name, space_name)
            app_metrics["state"] = self.__app_stats["0"]["state"]
            app_metrics["memory_usage_percentage"] = int(100*self.__app_stats["0"]["stats"]["usage"]["mem"]
                                                         / self.__app_stats["0"]["stats"]["mem_quota"])
            app_metrics["cpu_usage_percentage"] = int(self.__app_stats["0"]["stats"]["usage"]["cpu"]*100)
            app_metrics["disk_usage_percentage"] = int(100*self.__app_stats["0"]["stats"]["usage"]["disk"]
                                                       / self.__app_stats["0"]["stats"]["disk_quota"])
            max_instance, app_metrics["auto_scaled"] = self.get_max_instance(app_name, space_name)
            if max_instance == 0:
                app_metrics["instance_usage_percentage"] = 100
            else:
                app_metrics["instance_usage_percentage"] = int(100 * len(self.__app_stats) / int(max_instance))
            app_metrics["active_containers"] = len(self.__app_stats)

        else:
            app_metrics["state"] = self.__app_summary["state"]
            app_metrics["package_state"] = self.__app_summary["package_state"]
            app_metrics["staging_failed_reason"] = self.__app_summary["staging_failed_reason"]
            app_metrics["staging_failed_description"] = self.__app_summary["staging_failed_description"]
        self.get_max_instance(app_name, space_name)
        return app_metrics

    def get_metrics_urls(self, org_name):
        base_url = os.getenv("base_url", "((base_url))")
        org_guid = self.__pcf.get_org_guid(org_name)
        urls = []
        for space in self.__pcf.get_spaces():
            if space["organization_guid"] == org_guid:
                for app in self.__pcf.apps(space["name"], None):
                    url = "http://{}/spaces/{}/apps/{}/metrics".format(base_url, space["name"], app["name"])
                    urls.append(url)
        return urls

    def get_max_instance(self, app_name, space_name):
        info = self.__pcf.get_scaling_conf(space_name, app_name)
        return info["max_instances"], info["enabled"]

