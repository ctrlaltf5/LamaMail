#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import smtplib
import gnupg
import hashlib
import getpass
import subprocess
import email
import email.message
from pathlib import Path
from email.utils import formataddr
from datetime import datetime

# ========== 📁 Global Ayarlar ==========
GPG_HOME = str(Path.home() / ".lamamail" / "gpg")
MAILDIR = str(Path.home() / "Maildir")
USERS_DB = str(Path.home() / ".lamamail" / "users.db")

gpg = gnupg.GPG(gnupghome=GPG_HOME)
os.makedirs(GPG_HOME, exist_ok=True)
os.makedirs(MAILDIR + "/new", exist_ok=True)
os.makedirs(MAILDIR + "/cur", exist_ok=True)
os.makedirs(MAILDIR + "/tmp", exist_ok=True)
os.makedirs(Path(USERS_DB).parent, exist_ok=True)

# ========== 🔐 Şifreleme Fonksiyonları ==========
def md5_hash(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()

def encrypt_message(message, recipient):
    encrypted_data = gpg.encrypt(message, recipient)
    return str(encrypted_data) if encrypted_data.ok else None

def decrypt_message(encrypted_text):
    decrypted_data = gpg.decrypt(encrypted_text)
    return str(decrypted_data) if decrypted_data.ok else None

# ========== 👥 Kullanıcı Yönetimi ==========
def load_users():
    if not os.path.exists(USERS_DB):
        return {}
    with open(USERS_DB, 'r') as f:
        lines = f.read().splitlines()
    return {u.split(":")[0]: u.split(":")[1] for u in lines}

def save_user(username, hashed_pwd):
    with open(USERS_DB, 'a') as f:
        f.write(f"{username}:{hashed_pwd}\n")

def login():
    users = load_users()
    username = input("👤 Kullanıcı adı: ")
    password = getpass.getpass("🔑 Şifre: ")
    if username in users and users[username] == md5_hash(password):
        print("✅ Giriş başarılı.")
        return username
    print("❌ Giriş başarısız.")
    return None

def register():
    username = input("🆕 Kullanıcı adı: ")
    password = getpass.getpass("🔐 Şifre: ")
    save_user(username, md5_hash(password))
    print("✅ Kayıt tamam.")

# ========== 📤 Mail Gönderimi ==========
def send_mail():
    from_name = input("👤 Gönderici adı: ")
    from_email = input("📬 Gönderici mail (spoof edilebilir): ")
    to_email = input("🎯 Alıcı mail: ")
    subject = input("✉️ Konu: ")
    body = input("📝 Mesaj: ")

    encrypt = input("🔐 Şifrele (GPG)? (y/n): ").lower() == "y"
    if encrypt:
        body = encrypt_message(body, to_email)
        if not body:
            print("❌ Şifreleme başarısız.")
            return

    msg = email.message.EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr((from_name, from_email))
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP('localhost') as server:
            server.send_message(msg)
        print("✅ Mail gönderildi.")
    except Exception as e:
        print(f"❌ SMTP Hatası: {e}")

# ========== 📥 Gelen Kutusu ==========
def check_inbox():
    print("📬 Gelen kutusu:")
    for fname in os.listdir(MAILDIR + "/new"):
        with open(os.path.join(MAILDIR, "new", fname), 'r') as f:
            content = f.read()
            print("="*50)
            print(decrypt_message(content) or content)
            print("="*50)
            reply_option(fname, content)

# ========== 🔄 Yanıtla / İlet ==========
def reply_option(fname, original):
    opt = input("↩️ Yanıtla (r) | 📎 İlet (f) | ↩️ Geç (enter): ").lower()
    if opt == 'r':
        to_email = input("🎯 Alıcı (orijinal gönderici): ")
        subject = "RE: " + input("🔁 Yeni konu: ")
        msg = input("📝 Mesajınız: ")
        send_reply(to_email, subject, msg)
    elif opt == 'f':
        to_email = input("🎯 Alıcı (yeni): ")
        subject = "FW: " + input("🔁 Yeni konu: ")
        send_reply(to_email, subject, original)

def send_reply(to_email, subject, body):
    msg = email.message.EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'noreply@lamamail.local'
    msg['To'] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP('localhost') as server:
            server.send_message(msg)
        print("✅ Gönderildi.")
    except Exception as e:
        print(f"❌ SMTP Hatası: {e}")

# ========== 🖥️ Ana Menü ==========
def main_menu():
    print(r"""
     __        __   _                            _ 
     \ \      / /__| | ___ ___  _ __ ___   ___  | |
      \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | |
       \ V  V /  __/ | (_| (_) | | | | | |  __/ |_|
        \_/\_/ \___|_|\___\___/|_| |_| |_|\___| (_)

        🧅 L A M A M A I L   I S   A C T I V E 🧅
============================================================
|| SMTP Over Tor | No Logs | Spoof From | Terminal-Based ||
============================================================
Powered by: LINUX · POSTFIX · SMTPLIB · KACZYSNKI'S GHOST
""")
    print("🐑 LamaMail'e Hoşgeldin")
    print("[1] Giriş yap")
    print("[2] Kayıt ol")
    print("[3] Çıkış")

    choice = input("> ")
    if choice == '1':
        user = login()
        if user:
            user_dashboard()
    elif choice == '2':
        register()
        main_menu()
    else:
        exit()

def user_dashboard():
    while True:
        print("\n📡 Komutlar:")
        print("[1] Mail gönder")
        print("[2] Gelen kutusunu kontrol et")
        print("[3] Çıkış yap")
        cmd = input("> ")
        if cmd == '1':
            send_mail()
        elif cmd == '2':
            check_inbox()
        else:
            break

# ========== 🚀 Çalıştır ==========
if __name__ == "__main__":
    main_menu()

