#!/bin/bash

echo "🧅 Tor + Postfix + Dovecot + SMTP2GO Kurulumu Başlıyor..."

# 1. Gerekli paketleri kur
sudo apt update
sudo apt install -y tor postfix dovecot-core dovecot-imapd mailutils rsyslog logrotate

# 2. Tor yapılandırması
TOR_DIR="/var/lib/tor/lamamail_service"
sudo mkdir -p "$TOR_DIR"
sudo chown -R debian-tor:debian-tor "$TOR_DIR"
sudo chmod 700 "$TOR_DIR"

TORRC="/etc/tor/torrc"
if ! grep -q "$TOR_DIR" "$TORRC"; then
  echo "HiddenServiceDir $TOR_DIR" | sudo tee -a "$TORRC"
  echo "HiddenServicePort 25 127.0.0.1:25" | sudo tee -a "$TORRC"
  echo "HiddenServicePort 143 127.0.0.1:143" | sudo tee -a "$TORRC"
  echo "HiddenServicePort 587 127.0.0.1:587" | sudo tee -a "$TORRC"
fi

sudo systemctl restart tor
sleep 3

ONION=$(sudo cat "$TOR_DIR/hostname" 2>/dev/null || echo ".onion adres oluşturulamadı")

# 3. Postfix ayarları
sudo postconf -e "myhostname = $ONION"
sudo postconf -e "mydestination = localhost"
sudo postconf -e "home_mailbox = Maildir/"
sudo postconf -e "inet_interfaces = all"
sudo postconf -e "inet_protocols = all"
sudo postconf -e "smtp_sasl_auth_enable = yes"
sudo postconf -e "smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd"
sudo postconf -e "smtp_sasl_security_options = noanonymous"
sudo postconf -e "smtp_tls_security_level = may"
sudo postconf -e "smtp_use_tls = yes"
sudo postconf -e "relayhost = [mail.smtp2go.com]:587"

# 4. SMTP2GO kimlik bilgileri
echo "[mail.smtp2go.com]:587 your_name:your_api" | sudo tee /etc/postfix/sasl_passwd > /dev/null
sudo postmap /etc/postfix/sasl_passwd
sudo chmod 600 /etc/postfix/sasl_passwd /etc/postfix/sasl_passwd.db
sudo systemctl restart postfix

# 5. Dovecot ayarları
sudo sed -i 's|^#mail_location =.*|mail_location = maildir:~/Maildir|' /etc/dovecot/conf.d/10-mail.conf
sudo sed -i 's/^.*port = 0/    port = 143/' /etc/dovecot/conf.d/10-master.conf
sudo systemctl restart dovecot

# 6. Log rotate
if [ ! -f /etc/logrotate.d/mail ]; then
  echo "/var/log/mail.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 640 syslog adm
    sharedscripts
    postrotate
      /etc/init.d/rsyslog reload > /dev/null
    endscript
  }" | sudo tee /etc/logrotate.d/mail > /dev/null
fi

# 7. Servisleri otomatik başlat
sudo systemctl enable tor
sudo systemctl enable postfix
sudo systemctl enable dovecot

echo ""
echo "✅ LamaMail SMTP2GO ile hazır!"
echo "🌍 Onion Domainin: $ONION"
