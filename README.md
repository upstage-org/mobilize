# UpStage

[![CI](https://github.com/upstage-org/upstage/actions/workflows/devapp1.yml/badge.svg)](https://github.com/upstage-org/upstage/actions/workflows/devapp1.yml)

UpStage is a platform for cyberformance - remote players combine digital media in real-time for an online audience. All you need is a web browser!

In 2020, as part of the Mobilise/Demobilise project, UpStage is getting a complete rebuild. We are removing its dependency on Flash so that it will function on mobile devices, and making numerous enhancements. Please star the repository and join the team - all contributors welcome!

For more information, visit https://mobilise-demobilise.eu and https://upstage.org.nz/

# Documentation

[User Manual](https://docs.upstage.live/)

# Installation Guide

## Infrastructure

A complete instance of UpStage should consist of:

- **Upstage Service**: backend code written in Python, Flask, Graphene, SQLAlchemy. This service provides the necessary API Endpoint, mainly in GraphQL to manage stages/media/players and configurations such as foyer, permissions and notifications.
- **Dashboard**: frontend code written in Vue 3, Anime.js, Moveable, Bulma and many canvas operations. This is where most of the user interactions took place, such as the foyer, live stage, backstage and the admin section.
- **MQTT Broker**: this is the magic behind UpStage's performance work. The broker has many topics to be subscribed, such as `meta/demo/chat` can be used to deliveries chat messages between players and audiences in Demo Stage at the `meta` instance. The same broker can also be used for multiple instance of UpStage.
- **PostgresSQL**: our primary database, where all the data of players, stages, media, permissions, replays, configs,... are stored.
- **MongoDB**: we don't persist data in MongoDB, instead we use it as a queue for processing heavy computation and caching.
- **Event Archive Service**: since MQTT doesn't save all the messages that have ever been sent along it, we need to build a service that listens to every message and stores it to our Postgres database. You can run an instance of UpStage without event archive running, but all stage changes will be lost after a browser reload, and no replays would be saved.
- **Studio**: just another frontend code written in Vue 3, but using a more modern technology stack, including Vite, TypeScript, TailwindCSS, Antd and Apollo client. Studio focuses on a better media upload/edit workflow, providing a better UI/UX than the version that was created in `Dashboard`.
- **Nginx**: we use Nginx to serve uploaded media and front-end compiled source code as static files. It is also used to pass incoming requests to UpStage service.
- **Streaming Service**: we use the [Node Media Server](https://github.com/illuspas/Node-Media-Server) which is an open source streaming server built with Node.JS as our streaming service. This is a 3rd-party project but is considered part of the infrastructure of UpStage because we use it closely to broadcast streams and play them on stages.

## Setup

`PostgresSQL`, `MongoDB`, `Nginx` and `MQTT Broker` can be installed using the system package manager, we don't cover them in this section. For a mqtt broker, we recommend using [Mosquitto](https://github.com/eclipse/mosquitto).

1. Clone the repository

```bash
git clone https://github.com/upstage-org/upstage.git
```

2. Setup `UpStage Service`:

```bash
# Install dependencies
pip install -r requirements.pip

# Create the systemd service using our example configuration
cp config/prod/upstage.service /etc/systemd/system/upstage.service

# Start the service
systemctl start upstage.service

# Enable the service if you want it start automatically on boot
systemctl enable upstage.service
```

3. Setup `Studio`:

```bash
cd studio

# Install dependencies
yarn install
yarn genql (This requires Node 16)

# Build source
yarn build
```

Studio will be served at `/studio` path of our instance.

4. Setup `Event Archive Service`:

```bash
# Create the systemd service using our example configuration
cp config/prod/event_archive.service /etc/systemd/system/event_archive.service

# Start the service
systemctl start event_archive.service

# Enable the service if you want it start automatically on boot
systemctl enable event_archive.service
```

5. Setup `Streaming Service`:

```bash
# Clone the Node-Media-Server repository
git clone https://github.com/illuspas/Node-Media-Server.git

# Create the systemd service using our example configuration
cp config/dev/streaming.service /etc/systemd/system/upstage-streaming.service

# Start the service
systemctl start upstage-streaming.service

# Enable the service if you want it start automatically on boot
systemctl enable upstage-streaming.service
```

8. Setup `Upstage Send Email Token To Cient Server`:
- To allow a client in another domain to send Upstage emails, the upstage.live
server must know about this new client so it can handle inbound email requests.
The client must also know where to send its email requests and where to get its
tokens from. 

```
# Add the client server to ACCEPT_SERVER_SEND_EMAIL_EXTERNAL on upstage.live config file.
ACCEPT_SERVER_SEND_EMAIL_EXTERNAL=['some_url', 'some_other_url', ...]

# On the upstage.live app server, make sure this is running:
cp config/prod/upstage_email_token.service /etc/systemd/system/upstage_email_token.service

# Start the service
systemctl start upstage_email_token.service

# Enable the service if you want it start automatically on boot
systemctl enable upstage_email_token.service

# On the svc1.upstage.live server (not client svc1), poke a hole in the ufw firewall to allow access to the mongo db from the new client server:
ufw allow from <external_ip> to any port <mongo_port>

# On the new client server, make sure these are set in the config file:
FULL_DOMAIN (most be set everywhere)
SEND_EMAIL_SERVER (set to URL for upstage.live app server
MONGO_EMAIL_HOST = "external_IP_of_svc1.upstage.live"
MONGO_EMAIL_PORT = mongo_port_of_same_server
MONGO_EMAIL_DB = "mongo_db_name"

```

## Configurations

UpStage was designed to have multiple instances of it working independently. Each instance could have its own configurations set to get worked.

1. `UpStage Service` and `Event Archive Service` configurations

The two services load the same configurations, which is a Python file located at `config/settings/` folder

```bash
# Use our example config file as a template
cp config/settings/your_hostname.py config/settings/$HOSTNAME.py
```

There are many configurations here, here are the most importants:

```python
# PostgresSQL connection. You won't be able to read and write data without this property
DB_NAME=""
DB_USER=""
DB_PASSWD=""
DB_HOST=""
DB_PORT=5432
```

```python
# MongoDB connection. Event Archive won't be able to put messages in queue without this configuration setup properly, which can lead to inconsistent stage behavior
MONGO_HOST = ""
MONGO_PORT = 27018
MONGO_DB = "upstage"
EVENT_COLLECTION = "events"
```

```python
# Event Archive will use this MQTT connection to archive events
MQTT_BROKER = ""
MQTT_PORT = 1884
MQTT_TRANSPORT = "tcp"
MQTT_USER = ""
MQTT_PASSWORD = ""
PERFORMANCE_TOPIC_RULE = "#"
```

```python
# You can get these keys from running these python files below. Your users won't be able to log in if you change these keys after creating them, so don't touch them after generating them!
CIPHER_KEY='' # Paste the result from fernet_crypto.py
SECRET_KEY='' # Paste the result from running __init__.py
```

```python
# When setup Send Email Service, only the Upstage server has permission to send the email. The Client-server has to call the external API of the Upstage server.
# Upstage server will generate and send a token to each client server every 10 minutes. That token has expired in 10 minutes. Client-server stores that token in MongoDB and uses that token to call the sendEmailExternal API of the Upstage server
EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.gandi.net'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 465
SUPPORT_EMAILS = '' # A list admin email always in bcc
EMAIL_HOST_DISPLAY_NAME = 'UpStage Support'
ACCEPT_SERVER_SEND_EMAIL_EXTERNAL = ['http://127.0.0.1:8000/'] # This is setup only in app1 server, All client server endpoint having permission using Upstage Send Email service
```

```python
# When setuping Streaming Service, a secret key is recommended so that we can set up password protection and prevent your streaming server from being used by strangers. You will need to paste that key here so that we can generate QR codes with correct stream sign, only then the players will be able to broadcast.
STREAM_KEY=''
```

2. `Studio` configurations

Studio and dashboard share the same access token and configurations base. In other word, you don't have to set up separate environment for studio.

3. `Nginx` configurations

Redirect all `http` request from port 80 to the secured version with `https`

```nginx
server {
        server_name _;
        listen 80;
        rewrite ^ https://upstage.live$request_uri? permanent;
}
```

Setup SSL certificates and listen on port 443

```nginx
server {
        server_name upstage.live;
        listen 443 ssl;
        ssl_dhparam /etc/nginx/ssl/dhparam.pem;
        ssl_ecdh_curve secp384r1;
        ssl_certificate /etc/letsencrypt/live/upstage.live/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/upstage.live/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
```

Serve `Dashboard` on root path of our instance

```nginx
        location / {
            alias /home/upstage/upstage/dashboard/dist/;
            try_files $uri $uri/ /index.html;
        }
```

Serve `Studio` on `/studio` path of our instance. If you change the path, remember to update `VUE_APP_STUDIO_ENDPOINT` to match

```nginx
        location /studio {
            alias /home/upstage/upstage/studio/dist/;
            try_files $uri $uri/ /V4.0/studio/index.html;
        }
```

Serve user uploaded media in `/static` path. Caching is important in this config block because without caching, preload media before playing a performance won't work!

```nginx
       location /static {
            alias /home/upstage/upstage/uploads;
            expires off;
            add_header Cache-Control 'no-cache, must-revalidate';
        }

```

Finally, pass the incoming request to `UpStage Service`

```nginx
        location /api {
            uwsgi_pass unix:///home/upstage/uwsgi_sockets/upstage.socket;
            uwsgi_read_timeout 1800s;
            uwsgi_send_timeout 900s;
            uwsgi_ignore_client_abort on;
            include uwsgi_params;
            uwsgi_hide_header       Content-Security-Policy;
            uwsgi_hide_header       X-Content-Security-Policy;
        }
}
```

## Recipes

### Scaffolding demo content & base media

Execute the scaffold script at:

```bash
python3 scripts/devtools/scaffold-base-media.py
```

The script uses the same configuration as the `upstage.service`, so there is no need to do additional setup.

It will use the media inside `dashboard/demo` folder to create base media, the subfolder of the media will decide its type (for example, an image inside `dashboard/demo/avatar` folder will be uploaded as an avatar, while another image inside `dashboard/demo/prop` would be uploaded as a prop). You will be asked for a username to whom these media will belong. A demo stage will be created afterward, in which all these media are assigned as the default.

## Troubleshooting

### Stages offline when entering with firefox

If you are using firefox and doesn't have the red `LIVE` status on the top right when entering a stage although the stage is live using other browsers, it's because the version of Mosquitto (MQTT Broker) you are using doesn't use `libwebsockets` or it's using a version of `libwebsockets` that having an issue in protocol handling of HTTP2. Whilst Chromium does not attempt a HTTP2 connection in this case, Firefox tries it first and gets a denied reply from the server. More explanation can be found [here](https://www.bluhm-de.com/content/os-tools/en/applications/mqtt/websocket-connections-fail-with-javascript-paho-client.html).

The solution is to build `libwebsockets` and `mosquitto` from source and use it instead of the one provided by your distro.

Instruction on how to do this:

```bash
apt install libssl-dev xsltproc docbook-xsl
git clone https://github.com/warmcat/libwebsockets.git
cd libwebsockets
mkdir build
cd build
cmake .. -DLWS_WITH_HTTP2=OFF
make
make install
ldconfig
cd ../..
git clone https://github.com/eclipse/mosquitto.git
cd mosquitto
make install WITH_WEBSOCKETS=yes WITH_CJSON=no
sudo systemctl edit mosquitto.service
```

Put this into the override file of the service:

```ini
[Unit]
ConditionPathExists=/etc/mosquitto/mosquitto.conf
Requires=network.target

[Service]
Type=
Type=simple
ExecStart=
ExecStart=/usr/local/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
```

Finally restart the service

```bash
sudo systemctl restart mosquitto.service
```

## License

[GPL-3.0 License](https://github.com/upstage-org/upstage/blob/main/LICENSE)
