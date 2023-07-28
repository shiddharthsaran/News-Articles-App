

# Elasticsearch Deployment Documentation

## Introduction
This document provides step-by-step instructions for deploying Elasticsearch on a virtual machine (VM) with X-Pack security enabled. X-Pack security requires authentication with a username and password to access Elasticsearch.

### Prerequisites
- A virtual machine (VM) with the required ports (22, 80, 443, 9200) open.
- Internet connectivity on the VM to download packages.

## Step 1: Install Elasticsearch

1. Add Elastic's GPG key:
	```bash
	curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
	```
2. Add the Elastic repository to the sources list:
	```bash
	echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
	```
3. Update the package list:
	```bash
	sudo apt update
	```
4. Install Elasticsearch:
	```bash
	sudo apt install elasticsearch
	```
## Step 2: Configure Elasticsearch

1. Open the Elasticsearch configuration file for editing:
	```bash
	sudo nano /etc/elasticsearch/elasticsearch.yml
	```
3. Under the "Network" section, add the following lines:
	- ` network.host: 127.0.0.1`
	- `http.host: 0.0.0.0`

4. Add the following line at the end of the file to enable X-Pack security:
	 - `` xpack.security.enabled: true``

## Step 3: Start and Enable Elasticsearch

1. Start the Elasticsearch service:
	```bash
	sudo systemctl start elasticsearch
	```
3. Enable Elasticsearch to start on boot:
	```bash
	sudo systemctl enable elasticsearch
	```
## Step 4: Test Elasticsearch

1. To test Elasticsearch use the following command:
	```bash
	curl -X GET 'http://localhost:9200'
	```
	- Response should be:
	```json
	{
	  "name" : "instance-3",
	  "cluster_name" : "elasticsearch",
	  "cluster_uuid" : "otGi92qEQq2XksPTIYA7mQ",
	  "version" : {
	    "number" : "7.17.11",
	    "build_flavor" : "default",
	    "build_type" : "deb",
	    "build_hash" : "eeedb98c60326ea3d46caef960fb4c77958fb885",
	    "build_date" : "2023-06-23T05:33:12.261262042Z",
	    "build_snapshot" : false,
	    "lucene_version" : "8.11.1",
	    "minimum_wire_compatibility_version" : "6.8.0",
	    "minimum_index_compatibility_version" : "6.0.0-beta1"
	  },
	  "tagline" : "You Know, for Search"
	}
	```
## Step 5: Create a Superuser for X-Pack Security

1. Add a superuser with a username and password (replace `{user_name}` and `{password}` with your desired values):
	```bash
	sudo /usr/share/elasticsearch/bin/elasticsearch-users useradd {user_name} -p {password} -r superuser
	```
2.  Restart the Elasticsearch service:
	```bash
	sudo systemctl restart elasticsearch
	```
## Step 6: Test X-Pack Security

1. To test Elasticsearch without authentication, use the following command (it should not work):
	```bash
	curl -X GET 'http://localhost:9200'
	```
2. To test Elasticsearch with authentication, use the following command (replace `{user_name}` and `{password}` with the credentials you set earlier):
	```bash
	curl -u {user_name}:{password} -XGET 'http://localhost:9200'
	```
3. If the setup is correct, this command should work and return Elasticsearch information.



## Conclusion
Successfully deployed Elasticsearch with X-Pack security enabled on your virtual machine. Your Elasticsearch instance is now protected with authentication, and unauthorised access is restricted.









 
# Flask Server Deployment Documentation

This documentation outlines the steps to deploy a Flask server with Gunicorn and Nginx as a reverse proxy on Ubuntu.
### Prerequisites
- A virtual machine (VM) with the required ports (22, 80, 443, 5000) open.
- Internet connectivity on the VM to download packages.
## Step 1: Initial Server Setup

1. SSH into your Ubuntu server using the appropriate credentials.

2. Update the package list and install required packages:
	```bash
	sudo apt update
	sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
	sudo apt install python3-venv
	```
	
## Step 2: Create Project Directory and Virtual Environment

1. Create a directory for your project and navigate to it:
	```bash
	mkdir ~/{project_name}
	cd ~/{project_name}
	```

3. Set up a virtual environment for the project:
	```bash
	python3 -m venv {py_env_name}
	source {py_env_name}/bin/activate
	```
## Step 3: Install Required Python Packages

1. Install necessary Python packages using pip:
	```bash
	pip install wheel
	pip install gunicorn flask
	pip install elasticsearch python-dotenv
	```
## Step 4: Run the Flask Application

1. Create the main application file:
	```bash
	nano /{project_name}/{project_name}.py
	```

2.  Add your Flask application code to the file.
3. Allow Incoming Traffic on Port 5000
	```bash
	sudo ufw allow 5000
	```
4. Run the Flask Application
	```bash
	python {project_name}.py
	```
5. Flask app is running can be accessed through `http://{vm_external_ip}:5000`
6. Press CTRL-C to stop the Flask development server.
## Step 5: Create and Configure WSGI File
1. Create a wsgi.py file in your project directory:
	```bash
	nano ~/{project_name}/wsgi.py
	```
2. In the wsgi.py file, import the Flask instance from your application (replace `{project_name with}` the actual name of your Flask application file):
	```python
	from {project_name} import app
	if __name__ == "__main__":
	    app.run()
	```
3. Save the file and exit the text editor.

## Step 6: Run Gunicorn with WSGI
1. Change your working directory to your project folder:
	```bash
	cd ~/{project_name}
	```
2. Run Gunicorn with the wsgi.py file:
	```bash
	gunicorn --bind 0.0.0.0:5000 wsgi:app
	```
3. Flask app is running can be accessed through `http://{vm_external_ip}:5000`
4. Press CTRL-C to stop the Flask development server and deactivate python environment.
	```bash
	deactivate
	```
## Step 7: Set Up Gunicorn as Systemd Service
1. Create a systemd service file for Gunicorn:
	```bash
	sudo nano /etc/systemd/system/{project_name}.service
	```
2. Paste the following content into the file, replacing `{project_name}` and `{py_env_name}` with appropriate values:
	```ini
	[Unit]
	Description=Gunicorn instance to serve {project_name}
	After=network.target

	[Service]
	User=ubuntu
	Group=www-data
	WorkingDirectory=/home/ubuntu/{project_name}
	Environment="PATH=/home/ubuntu/{project_name}/{py_env_name}/bin"
	ExecStart=/home/ubuntu/{project_name}/{py_env_name}/bin/gunicorn --workers 3 --bind unix:{project_name}.sock -m 007 wsgi:app

	[Install]
	WantedBy=multi-user.target
	```
3. Start and enable the Gunicorn service:
	```bash
	sudo systemctl start {project_name}
	sudo systemctl enable {project_name}
	sudo systemctl status {project_name}
	```


## Step 8: Configure Nginx as Reverse Proxy
1. Create an Nginx server block configuration file:
	```bash
	sudo nano /etc/nginx/sites-available/{project_name}
	```
2. Add the following server block configuration, replacing `{project_name}` and `{vm_external_ip}` with appropriate values:
	```nginx
	server {
	    listen 80;
	    server_name {vm_external_ip};

	    location / {
	        include proxy_params;
	        proxy_pass http://unix:/home/ubuntu/{project_name}/{project_name}.sock;
	    }
	}
	```
3. Create a symbolic link and check the Nginx configuration:
	```bash
	sudo ln -s /etc/nginx/sites-available/{project_name} /etc/nginx/sites-enabled
	sudo nginx -t
	```
4. Restart Nginx to apply the changes:
	```bash
	sudo systemctl restart nginx
	```
## Step 9: Firewall Configuration
1. Remove the temporary firewall rule for port 5000:
	```bash
	sudo ufw delete allow 5000
	```
2. Allow Nginx traffic through the firewall:
	```bash
	sudo ufw allow 'Nginx Full'
	```
## Conclusion
Flask server is now deployed with Gunicorn and Nginx as a reverse proxy.


