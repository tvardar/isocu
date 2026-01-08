#!/bin/bash

# --- PROJE BİLGİLERİ ---
APP_NAME="isocu"
EXE_NAME="Isocu" 
ICON_NAME="isocu"
VERSION="1.0"
ARCH="amd64"
MAINTAINER="Tarik Vardar <tarikvardar@gmail.com>"
WEBSITE="https://www.tarikvardar.com.tr"
DESCRIPTION="Klasor ve dosyalardan ISO olusturma araci."
LICENSE="MIT License"

# --- KLASÖR TANIMLARI ---
BUILD_DIR="build_deb"
OUTPUT_DEB="${APP_NAME}_${VERSION}_${ARCH}.deb"
LOCAL_DEPS="bagimliliklar"

echo "🚀 ISOCU PAKETLEME SİHİRBAZI BAŞLATILIYOR (v$VERSION)..."

# ==============================================================================
# 1. TEMİZLİK
# ==============================================================================
echo "🧹 Temizlik yapılıyor..."
rm -rf build dist $BUILD_DIR *.deb *.spec

# ==============================================================================
# 2. BAĞIMLILIKLARI VE PYINSTALLER'I YEREL KLASÖRE İNDİR
# ==============================================================================
echo "⬇️  Bağımlılıklar ve PyInstaller '$LOCAL_DEPS' klasörüne indiriliyor..."

if ! command -v pip3 &> /dev/null; then
    sudo apt-get update && sudo apt-get install -y python3-pip
fi

mkdir -p $LOCAL_DEPS

# 1. Proje bağımlılıklarını indir
pip3 install -r requirements.txt --target "$LOCAL_DEPS" --upgrade --break-system-packages

# 2. PyInstaller'ı da AYNI yere indir (Kritik Düzeltme)
pip3 install pyinstaller --target "$LOCAL_DEPS" --upgrade --break-system-packages

# Gereksiz önbellekleri temizle
find "$LOCAL_DEPS" -name "__pycache__" -type d -exec rm -rf {} +
find "$LOCAL_DEPS" -name "*.dist-info" -type d -exec rm -rf {} +

# ==============================================================================
# 3. PYINSTALLER İLE DERLEME
# ==============================================================================
echo "📦 PyInstaller ile tek parça haline getiriliyor..."
export PYTHONPATH="$(pwd)/$LOCAL_DEPS:$PYTHONPATH"

# PyInstaller modül olarak çağırılıyor, ancak yolu PYTHONPATH'te olmalı
python3 -m PyInstaller main.py \
    --name="$EXE_NAME" \
    --onedir \
    --windowed \
    --noconsole \
    --clean \
    --noconfirm \
    --strip \
    --paths="$LOCAL_DEPS" \
    --add-data="assets:assets" \
    --icon="assets/icon.png" \
    --contents-directory="libs" \
    --hidden-import="pycdlib" \
    --hidden-import="PIL" \
    --hidden-import="PyQt6" \
    --collect-all="pycdlib" \
    --collect-all="PIL" \
    --collect-all="PyQt6"

if [ ! -d "dist/$EXE_NAME" ]; then
    echo "❌ HATA: Derleme başarısız oldu!"
    exit 1
fi

# ==============================================================================
# 4. DEB PAKET YAPISI OLUŞTURMA
# ==============================================================================
echo "📂 .deb paket yapısı kuruluyor..."

mkdir -p $BUILD_DIR/DEBIAN
mkdir -p $BUILD_DIR/opt/$APP_NAME
mkdir -p $BUILD_DIR/usr/bin
mkdir -p $BUILD_DIR/usr/share/applications
mkdir -p $BUILD_DIR/usr/share/icons/hicolor/512x512/apps
mkdir -p $BUILD_DIR/usr/share/pixmaps
mkdir -p $BUILD_DIR/usr/share/doc/$APP_NAME

# Uygulama Dosyalarını Kopyala
cp -r dist/$EXE_NAME/* $BUILD_DIR/opt/$APP_NAME/

# İkonları Yerleştir
cp assets/icon.png $BUILD_DIR/usr/share/icons/hicolor/512x512/apps/$ICON_NAME.png
cp assets/icon.png $BUILD_DIR/usr/share/pixmaps/$ICON_NAME.png

# Lisans Dosyası (MIT)
cat > $BUILD_DIR/usr/share/doc/$APP_NAME/copyright << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: $APP_NAME
Source: $WEBSITE

Files: *
Copyright: 2025 $MAINTAINER
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
EOF

# ==============================================================================
# 5. BAŞLATICI VE DESKTOP DOSYASI
# ==============================================================================
cat > $BUILD_DIR/usr/bin/$APP_NAME << EOF
#!/bin/bash
export QT_QPA_PLATFORM=xcb
cd /opt/$APP_NAME
./$EXE_NAME "\$@"
EOF
chmod 755 $BUILD_DIR/usr/bin/$APP_NAME

cat > $BUILD_DIR/usr/share/applications/$APP_NAME.desktop << EOF
[Desktop Entry]
Name=İsocu
GenericName=ISO Oluşturucu
Comment=Klasörden ISO Dönüştürme Aracı
Exec=/usr/bin/$APP_NAME
Icon=$ICON_NAME
Terminal=false
Type=Application
Categories=Utility;DiscBurning;Filesystem;
StartupNotify=true
Keywords=iso;image;burn;create;
EOF
chmod 644 $BUILD_DIR/usr/share/applications/$APP_NAME.desktop

# ==============================================================================
# 6. CONTROL DOSYASI
# ==============================================================================
cat > $BUILD_DIR/DEBIAN/control << EOF
Package: $APP_NAME
Version: $VERSION
Architecture: $ARCH
Maintainer: $MAINTAINER
Homepage: $WEBSITE
Depends: libc6, libgl1, libegl1, libxcb-cursor0, libxcb-xinerama0, libnss3, libasound2
Section: utils
Priority: optional
Description: $DESCRIPTION
 Pardus ve Debian tabanli sistemler icin basit ve guclu ISO olusturma araci.
 .
 Lisans: $LICENSE
EOF
chmod 755 $BUILD_DIR/DEBIAN/control

# ==============================================================================
# 7. PAKETLEME VE BİTİŞ
# ==============================================================================
echo "🔒 İzinler ayarlanıyor..."
chmod -R 755 $BUILD_DIR/opt/$APP_NAME
chmod -R 755 $BUILD_DIR/DEBIAN

echo "📦 .deb paketi oluşturuluyor..."
dpkg-deb --root-owner-group --build $BUILD_DIR $OUTPUT_DEB

echo ""
echo "✅ İŞLEM BAŞARIYLA TAMAMLANDI!"
echo "📂 Oluşturulan Paket: $OUTPUT_DEB"
echo "ℹ️  Kurulum için: sudo dpkg -i $OUTPUT_DEB"