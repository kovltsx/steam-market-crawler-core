# Overview

Steam Market Bot (Core)

## Technologies

- **Python** Programming Language
- **Flask** Webserver
- **python-socketio** Real-time communications
- **Redis** Message Broker
- **Selenium** Browser Automation
- **Chromium** Headless Browser

## Setup

Download chromium and chromedriver v87.0.4280.88

##### Chromium for 64-bit Windows

https://github.com/macchrome/winchrome/releases/download/v87.0.4280.88-r812852-Win64/ungoogled-chromium-87.0.4280.88-1_Win64.7z

##### Chromium and chromedriver for 64-bit Linux

```
sudo apt install chromium-browser
```

##### Chromedriver for both platforms

https://chromedriver.storage.googleapis.com/index.html?path=87.0.4280.88/

### Create files at /src/ and add data

###### proxies.txt

```
123.123.123.123:1234
...
```

###### queries.txt

```
five seven case hardened field tested
...
```

### Run

###### Development

```
rq worker
python run.py
```

###### Production

Load uwsgi server application on boot with a Systemd unit file. Modify paths in /src/services/

```
mv services/steam-market-bot.service /etc/systemd/system
sudo systemctl start steam-market-bot
sudo systemctl enable steam-market-bot
```

Configuring Nginx to Proxy Requests

```
sudo cp services/steam-market-bot /etc/nginx/sites-available/steam-market-bot
sudo ln -s /etc/nginx/sites-available/steam-market-bot /etc/nginx/sites-enabled
sudo nginx -t # test any typing errors
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'
```

Visit on your browser:

```
http://your_domain/
```
