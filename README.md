# LamaMail
# 🧅 LamaMail

## 📡 Terminal tabanlı, Tor destekli, SMTP2GO entegreli mail sistemi  
> **Powered by Postfix + Dovecot + Python + Tor + SMTP2GO**

---

## 📦 Özellikler

- 🧅 .onion domain ile kendi gizli mail sunucunu kur
- 📬 SMTP2GO ile GMail, Outlook gibi servislerden bağımsız olarak mail gönder
- 💻 Terminal arayüzlü mail gönderici (`lamamail.py`)
- 🛑 Log yok, kayıt yok, gözetim yok
- 🧠 Kurulumu tek komutla hallet(!)
- 🧰 İleri düzeyde spoofing ve GPG şifreleme (opsiyonel)

---

## 🔧 Kurulum

> Linux makinanda terminali aç ve aşağıdaki adımları takip et:

### 1️⃣ Gereksinimleri yükle

```bash
sudo apt update
sudo apt install -y tor postfix dovecot-core dovecot-imapd mailutils python3 python3-pip gpg
pip install faker rich gnupg
git clone https://github.com/ctrlaltf5/LamaMail
cd LamaMail
chmod +x lamamail_setup.sh
./lamamail_setup.sh
python3 lamamail.py
