#!/bin/bash
set -e

echo "============================================="
echo "Exposys AWS Server Setup Script"
echo "============================================="

# 1. Update and install system dependencies
echo "[1/6] Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx postgresql postgresql-contrib build-essential curl unzip

# 2. Install Node.js LTS and PM2
echo "[2/6] Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pm2

# 3. Configure PostgreSQL
echo "[3/6] Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE exposys_db;" || echo "Database may already exist"
sudo -u postgres psql -c "CREATE USER exposys_app WITH PASSWORD 'your_db_password_here';" || echo "User may already exist"
sudo -u postgres psql -c "ALTER ROLE exposys_app SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE exposys_app SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE exposys_app SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE exposys_db TO exposys_app;"

cd /var/www/exposys

# 4. Setup Python Virtual Environment and initialize DB
echo "[4/6] Setting up Python Environment & Initializing DB..."
sudo mkdir -p uploads
sudo chown -R ubuntu:www-data /var/www/exposys
sudo chmod -R 775 /var/www/exposys/uploads

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

cp aws_deployment/.env.template .env

export FLASK_APP=app.py
python3 -c "from app import create_app, db, seed_data; app=create_app(); app.app_context().push(); db.create_all(); seed_data()"

# 5. Setup Node.js Backend
echo "[5/6] Setting up Node.js Certificate Backend..."
cd certificate_system/backend
npm install
pm2 start ../../aws_deployment/ecosystem.config.js
pm2 save
pm2 startup systemd -u ubuntu --hp /home/ubuntu | tail -n 1 | sudo bash
cd /var/www/exposys

# 6. Configure Systemd and Nginx
echo "[6/6] Configuring Systemd and Nginx..."
sudo cp aws_deployment/exposys.service /etc/systemd/system/
sudo systemctl start exposys
sudo systemctl enable exposys

sudo cp aws_deployment/exposys.nginx.conf /etc/nginx/sites-available/exposys
sudo ln -sf /etc/nginx/sites-available/exposys /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

sudo mkdir -p /var/log/exposys
sudo chown -R www-data:www-data /var/log/exposys

echo "============================================="
echo "Server setup complete! Application is LIVE."
echo "============================================="
