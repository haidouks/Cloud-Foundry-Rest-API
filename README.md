# Dockerized Python Flask API for Cloud Foundry

Dockerized Cloud Foundry Restfull API


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 


### Prerequisites

Please follow the steps below before you build the code;

```
git clone https://github.com/haidouks/cloud_foundry_python_api.git
cd cloud_foundry_python_api
```

Then you need to edit Dockerfile for the following environment variables

```
ENV user="canald@gmail.com"
ENV password="MyPass"
ENV api_endpoint="https://api.run.pivotal.io"
```

Build dockerfile
```
docker build . -t cloud_foundry_python_api
```


### Run the API

Python Api listens port 8081, run container on port 8080

```
docker run cloud_foundry_python_api -d -p 8080:8080
```

Browse url `http://localhost:8080` on your favorite browser.

## Available Methods

* List Buildpacks   : `GET /buildpacks`
* List Spaces       : `GET /spaces`
* View Space        : `GET /spaces/<space_name>`
* View Service Instances in Space        : `GET /spaces/<space_name>/service_instances`
* List Apps         : `GET /spaces/<space_name>/apps`
* App Summary       : `GET /spaces/<space_name>/apps/<app_name>/summary`
* App Status        : `GET /spaces/<space_name>/apps/<app_name>/stats`
* App Metrics       :  `GET /spaces/<space_name>/apps/<app_name>/metrics`
* App Buildpack       : `GET /spaces/<space_name>/apps/<app_name>/buildpacks`
* List App Service Bindings: `GET /spaces/<space_name>/apps/<app_name>/service_bindings`
* Service Binding's Detail: `GET /spaces/<space_name>/apps/<app_name>/service_bindings/<service_binding_name>`
* Remove Service Binding from App: `DELETE /spaces/<space_name>/apps/<app_name>/service_bindings/<service_binding_name>`
* List Metrics Urls : `GET /metrics_urls/<org_name>`
* List Organizations : `GET /organizations`
* View Organizations' Properties : `GET /organizations/<org_name>`
* List Buildpacks   : `GET /buildpacks`
* Space Service Binding's Detail: `GET /spaces/<space_name>/service_bindings/<service_binding_name>`
* List Service Keys: `GET /service_keys`
* Get CF Api Url: `POST /api_url`

## Examples:

### Example 1
For the secure methods, token should be specified in header.
`curl http://localhost:8080/spaces/mySpace/apps/myApp/summary -H "Authorization  : token DevOps123"`

### Example 2
For getting any CF Api Url, full path of the api should be provided. 
`curl http://localhost:8080/api_url -d "url=http://api.run.pivotal.io/v2/spaces/add2e0a1-afbd-4166-a515-78f4fbf3279d" -X POST -H "Authorization  : token DevOps123"`
