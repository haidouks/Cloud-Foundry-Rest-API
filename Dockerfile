FROM python:3
LABEL  maintainer="cansinaldanmaz@gmail.com"
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --upgrade --force-reinstall --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "./router.py" ]
