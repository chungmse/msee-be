# msee-be

A project of © MSE19HN-G1

## Setup on Ubuntu 24.04 LTS server

### Init server

```
Username: chungnv
Password: Mse123456!
```

```
adduser chungnv
usermod -aG sudo chungnv
ufw app list && ufw allow OpenSSH && ufw enable
rsync --archive --chown=chungnv:chungnv ~/.ssh /home/chungnv
sudo vi /etc/ssh/sshd_config
    PermitRootLogin no
    PasswordAuthentication no
    ChallengeResponseAuthentication no
sudo service ssh restart
sudo apt update -y && sudo apt upgrade -y
sudo service apache2 stop && sudo apt remove apache2 apache2-utils -y && sudo apt purge apache2 -y && sudo apt autoremove -y
sudo reboot
```

### Python

Ready to use

### Nginx

```
sudo apt update -y && sudo apt install nginx -y
sudo ufw allow 'Nginx HTTP' && sudo ufw allow 'Nginx HTTPS'

sudo apt install certbot python3-certbot-nginx -y
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
sudo certbot certonly --nginx -d msee-api.mse19hn.com

sudo nano /etc/nginx/sites-available/msee-api.mse19hn.com
server {
    listen 443 ssl http2;
    server_name msee-api.mse19hn.com;
    ssl_certificate /etc/letsencrypt/live/msee-api.mse19hn.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/msee-api.mse19hn.com/privkey.pem;
    ssl_session_cache shared:SSL:50m;
    ssl_session_timeout 1d;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers EECDH+CHACHA20:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    ssl_stapling on;
    ssl_stapling_verify on;
    add_header Strict-Transport-Security "max-age=31536000" always;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
}

sudo ln -s /etc/nginx/sites-available/msee-api.mse19hn.com /etc/nginx/sites-enabled/
sudo service nginx restart
```

### MongoDB

```
sudo apt install gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Redis

```
sudo apt install redis-server -y
sudo systemctl enable redis-server.service
```

### RabbitMQ

https://www.rabbitmq.com/docs/install-debian#apt-cloudsmith

### Nodejs

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install --lts
```

### PM2

```
npm install -g pm2
```

### msee-be

```
cd /myprojects
git clone https://github.com/chungmse/msee-be.git
sudo chown -R chungnv:chungnv /myprojects/msee-be && sudo chmod -R 755 /myprojects/msee-be
cd msee-be

sudo apt install python3-pip -y
sudo rm /usr/lib/python3.12/EXTERNALLY-MANAGED
pip install pymongo redis librosa uvicorn fastapi pika python-multipart

python3 utils/reset.py
Import msee.settings.json
Import msee.songs.json

python3 utils/extract_features.py
python3 utils/create_caches.py

pm2 start main.py --name "msee-be-main"
pm2 start workers/recognize_worker.py --name "msee-be-recognize_worker"

pm2 save
pm2 startup
```
