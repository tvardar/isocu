#!/bin/bash

# Hata olursa durdur
set -e

# --- AYARLAR ---
REPO_URL="https://github.com/tvardar/isocu.git"
COMMIT_MSG="isocu v1.0 Kararlı Sürüm Yayını 🚀"
GIT_NAME="Tarık Vardar"
GIT_EMAIL="tarikvardar@gmail.com"
YEAR="2026"

echo "----------------------------------------------------------------"
echo "📀 isocu GitHub Dağıtım Sihirbazı (v1.0)"
echo "----------------------------------------------------------------"

# 1. DOSYA İZİNLERİNİ DÜZELT
echo "[+] Dosya sahipliği ve izinleri düzeltiliyor..."
if [ "$SUDO_USER" ]; then
    chown -R $SUDO_USER:$SUDO_USER .
fi

# 2. GIT KİMLİK AYARLARI
echo "[+] Git kimlik ayarları yapılıyor..."
git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"

# 3. .gitignore OLUŞTUR
echo "[+] .gitignore dosyası oluşturuluyor..."
cat <<EOF > .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# Sanal Ortam
venv/
env/

# PyInstaller & Derleme
build/
dist/
*.spec
build_deb/

# Paketler
*.deb
*.iso

# IDE
.idea/
.vscode/
.DS_Store
EOF

# 4. LICENSE (MIT) OLUŞTUR
echo "[+] LICENSE (MIT) dosyası oluşturuluyor..."
cat <<EOF > LICENSE
MIT License

Copyright (c) $YEAR $GIT_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# 5. README.md OLUŞTUR
echo "[+] README.md oluşturuluyor (Ekran görüntüleri ile)..."
cat <<EOF > README.md
# 📀 isocu - Modern ISO Oluşturma Aracı

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Pardus%20%7C%20Debian-orange.svg)

**isocu**, Linux (Pardus/Debian) sistemler için geliştirilmiş, klasör ve dosyalarınızı tek tıkla **ISO formatına** dönüştüren, modern arayüzlü ve kullanıcı dostu bir araçtır.

Özellikle Windows/Linux uyumluluğu (Joliet/RockRidge) ve büyük dosya desteği (UDF) ile standartların ötesinde bir çözüm sunar.

## 📸 Ekran Görüntüleri

| **Ana Ekran** | **Hakkında ve Güncelleme** |
|:---:|:---:|
| ![Ana Ekran](screenshots/1.png) | ![Hakkında](screenshots/2.png) |
| *Sürükle-Bırak destekli modern arayüz* | *Otomatik güncelleme kontrolü* |

## 🚀 Özellikler

* **📂 Akıllı İsimlendirme:** Türkçe karakter, boşluk veya parantez içeren dosya isimlerini bozmadan ISO standardına (ISO 9660) uygun hale getirir.
* **💾 Büyük Dosya Desteği (UDF 2.60):** 4 GB üzerindeki dosyaları (oyun setup dosyaları, veritabanı yedekleri vb.) sorunsuz işler.
* **📀 Bootable ISO:** Önyüklenebilir (Bootable) ISO oluşturma desteği.
* **🔐 Checksum Hesaplayıcı:** Oluşturulan ISO'nun doğruluğunu SHA256 ile kontrol etme aracı.
* **🖥️ Modern Arayüz:** PyQt6 ile geliştirilmiş, sürükle-bırak destekli, karanlık mod uyumlu (Dark Theme) şık tasarım.
* **🔄 Arkaplan İşlemleri:** ISO oluşturma sırasında arayüz donmaz, sistem tepsisine (System Tray) küçülebilir.
* **🐧 Linux & Windows Uyumu:** Oluşturulan ISO'lar hem Linux (Rock Ridge) hem de Windows (Joliet) sistemlerde sorunsuz çalışır.
* **⚡ Tek Pencere (Single Instance):** Uygulama zaten açıksa, ikinci kez tıklandığında yenisini açmaz, mevcut olanı öne getirir.

## 📦 Kurulum

### Yöntem 1: .deb Paketi ile Kurulum (Önerilen)
Releases sayfasından en son \`.deb\` paketini indirin ve kurun:
\`\`\`bash
sudo dpkg -i isocu_1.0_amd64.deb
\`\`\`

### Yöntem 2: Kaynak Koddan Çalıştırma
\`\`\`bash
# 1. Depoyu klonlayın
git clone https://github.com/tvardar/isocu.git
cd isocu

# 2. Sanal ortam oluşturun ve aktif edin
python3 -m venv venv
source venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Çalıştırın
python3 main.py
\`\`\`

## 🛠️ Kullanılan Teknolojiler
* **Python 3**
* **PyQt6** (GUI)
* **pycdlib** (ISO İşlemleri)
* **Pillow** (Görsel İşleme)
* **Requests** (Güncelleme Kontrolü)
* **PyInstaller** (Paketleme)

## ⚖️ Lisans
Bu proje **MIT Lisansı** ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

## 👨‍💻 Geliştirici
**Tarık Vardar** - [Web Sitesi](https://www.tarikvardar.com.tr) | [GitHub](https://github.com/tvardar)
EOF

# 6. GIT İŞLEMLERİ
echo "[+] Git deposu hazırlanıyor..."

# .git klasörü varsa temizle (Temiz başlangıç)
rm -rf .git

git init
git add .
git commit -m "$COMMIT_MSG"
git branch -M main
git remote add origin "$REPO_URL"

echo "----------------------------------------------------------------"
echo "🚀 GITHUB'A YÜKLENİYOR (FORCE PUSH)..."
echo "NOT: Parola sorduğunda 'Personal Access Token' giriniz."
echo "----------------------------------------------------------------"

git push -u origin main --force

echo ""
echo "✅ İŞLEM BAŞARIYLA TAMAMLANDI!"
echo "👉 Projeniz burada: $REPO_URL"