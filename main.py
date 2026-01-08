import sys
import os
import time
import re
import requests
import subprocess
import webbrowser
import hashlib 
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QProgressBar, QTextEdit, QMessageBox, QLineEdit,
                             QSystemTrayIcon, QMenu, QDialog, QFrame, QMenuBar, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QIcon, QAction, QDragEnterEvent, QDropEvent, QCursor, QPixmap
from PyQt6.QtNetwork import QLocalServer, QLocalSocket 
import pycdlib
from pathlib import Path

# --- UYGULAMA BİLGİLERİ ---
APP_NAME = "isocu"
APP_ID = "com.tarikvardar.isocu"
APP_VERSION = "v1.0" 
APP_TITLE = f"{APP_NAME} {APP_VERSION}"

# GITHUB AYARLARI
GITHUB_USER = "tvardar"
GITHUB_REPO = "isocu"

# --- YARDIMCI FONKSİYONLAR ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def calculate_checksum(file_path, algorithm="sha256"):
    """Dosyanın hash değerini hesaplar"""
    hash_func = hashlib.sha256() if algorithm == "sha256" else hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return f"Hata: {str(e)}"

# --- GÜNCELLEME KONTROLCÜSÜ ---
class GuncellemeKontrolcusu(QThread):
    guncelleme_var_sinyali = pyqtSignal(str, str, str)
    hata_sinyali = pyqtSignal(str)
    
    def __init__(self, mevcut_surum):
        super().__init__()
        self.mevcut_surum = mevcut_surum
        self.API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

    def run(self):
        try:
            response = requests.get(self.API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").strip()
                download_url = ""
                body = data.get("body", "Yeni özellikler.")

                for asset in data.get("assets", []):
                    if asset["name"].endswith(".deb"):
                        download_url = asset["browser_download_url"]
                        break
                
                if latest_version:
                    try:
                        def clean_ver(v): return int(re.sub(r'[^0-9]', '', v))
                        v_mevcut = clean_ver(self.mevcut_surum)
                        v_yeni = clean_ver(latest_version)
                    except:
                        v_mevcut, v_yeni = 0, 0
                    
                    if v_yeni > v_mevcut and download_url:
                        self.guncelleme_var_sinyali.emit(latest_version, body, download_url)
                    else:
                        self.hata_sinyali.emit("GUNCEL")
            else:
                self.hata_sinyali.emit(f"Hata: {response.status_code}")
        except Exception as e:
            self.hata_sinyali.emit(str(e))

# --- HAKKINDA PENCERESİ ---
class HakkindaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hakkında")
        self.setFixedSize(600, 600)
        self.setStyleSheet("background-color: #1e272e; color: #d2dae2;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card = QFrame()
        card.setStyleSheet("background-color: transparent; border: 1px solid #555555; border-radius: 20px;")
        cl = QVBoxLayout(card)
        cl.setSpacing(10)
        cl.setContentsMargins(40, 30, 40, 30)
        
        icon_path = resource_path('assets/icon.png')
        if os.path.exists(icon_path):
            img = QLabel()
            pix = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img.setPixmap(pix)
            img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img.setStyleSheet("border: none; margin-bottom: 5px;")
            cl.addWidget(img)

        lbl_baslik = QLabel(APP_NAME.upper())
        lbl_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_baslik.setStyleSheet("font-size: 24pt; font-weight: 900; letter-spacing: 2px; border: none; color: #3498db;")
        cl.addWidget(lbl_baslik)

        lbl_surum = QLabel(f"Sürüm {APP_VERSION} (Stable)")
        lbl_surum.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_surum.setStyleSheet("font-size: 11pt; font-weight: bold; color: #f39c12; border: none;")
        cl.addWidget(lbl_surum)

        desc = QLabel("Seçtiğiniz dosya ve klasörlerden ISO oluşturma aracı.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 11pt; color: #ecf0f1; border: none; margin-bottom: 10px;")
        cl.addWidget(desc)

        # Güncelleme Butonu
        self.btn_update = QPushButton("Güncellemeleri Kontrol Et")
        self.btn_update.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_update.setStyleSheet("""
            QPushButton { background-color: #2c3e50; color: white; border: 1px solid #34495e; padding: 8px; border-radius: 5px; }
            QPushButton:hover { background-color: #34495e; }
        """)
        self.btn_update.clicked.connect(self.check_update)
        cl.addWidget(self.btn_update)

        # Linkler ve Geliştirici
        dev_info = """
        <style>
            a { color: #3498db; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
        </style>
        <p style='font-size:14px; margin-top:10px;'>
            Geliştirici: <b>Tarık Vardar</b><br>
            <a href='https://www.tarikvardar.com.tr'>www.tarikvardar.com.tr</a> | 
            <a href='https://github.com/tvardar'>github.com/tvardar</a>
        </p>
        """
        lbl_dev = QLabel(dev_info)
        lbl_dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_dev.setOpenExternalLinks(True)
        lbl_dev.setStyleSheet("border: none; color: #ecf0f1;")
        cl.addWidget(lbl_dev)

        # Lisans ve Uyarı
        lbl_lisans = QLabel(
            "Bu yazılım <b>MIT Lisansı</b> altında özgürce dağıtılmaktadır.<br><br>"
            "<span style='color:#e74c3c; font-style:italic; font-size:9pt;'>"
            "YASAL UYARI: Bu program yararlı olması ümidiyle dağıtılmaktadır, "
            "ancak <b>KESİNLİKLE HİÇBİR GARANTİSİ YOKTUR</b>. "
            "Ticari elverişlilik veya belirli bir amaca uygunluk dahil olmak üzere, "
            "açık veya zımni hiçbir garanti verilmez. Kullanımdan doğabilecek "
            "tüm riskler kullanıcıya aittir."
            "</span>"
        )
        lbl_lisans.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_lisans.setWordWrap(True)
        lbl_lisans.setStyleSheet("border: 1px dashed #555; padding: 10px; border-radius: 5px; margin-top: 10px;")
        cl.addWidget(lbl_lisans)
        
        layout.addWidget(card)
        self.parent_window = parent

    def check_update(self):
        self.btn_update.setText("Kontrol Ediliyor...")
        self.btn_update.setEnabled(False)
        self.checker = GuncellemeKontrolcusu(APP_VERSION)
        self.checker.guncelleme_var_sinyali.connect(self.parent_window.show_update_dialog)
        self.checker.hata_sinyali.connect(lambda msg: self.btn_update.setText("Sürüm Güncel (v1.0)" if msg=="GUNCEL" else "Hata"))
        self.checker.finished.connect(lambda: self.btn_update.setEnabled(True))
        self.checker.start()

# --- WORKER THREAD (ISO) ---
class IsoWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, source_folder, iso_path, volume_label, boot_image=None):
        super().__init__()
        self.source_folder = source_folder
        self.iso_path = iso_path
        self.volume_label = volume_label
        self.boot_image = boot_image
        self.is_running = True
        self.used_iso_names = set()

    def get_safe_iso_name(self, name):
        base, ext = os.path.splitext(name)
        safe_base = re.sub(r'[^A-Z0-9_]', '_', base.upper())[:50]
        safe_ext = re.sub(r'[^A-Z0-9_]', '_', ext.upper())
        candidate = f"{safe_base}{safe_ext}"
        counter = 1
        while candidate in self.used_iso_names:
            candidate = f"{safe_base[:45]}_{counter}{safe_ext}"
            counter += 1
        self.used_iso_names.add(candidate)
        return candidate

    def run(self):
        try:
            self.log.emit(f"🚀 {APP_NAME} başlatılıyor...")
            safe_vol = re.sub(r'[^A-Z0-9_]', '_', self.volume_label.upper())[:32]
            
            iso = pycdlib.PyCdlib()
            iso.new(interchange_level=3, joliet=3, rock_ridge='1.09', udf='2.60', vol_ident=safe_vol)

            if self.boot_image and os.path.exists(self.boot_image):
                self.log.emit(f"💿 Boot imajı ekleniyor: {os.path.basename(self.boot_image)}")
                boot_iso_name = 'BOOT.IMG'
                iso.add_file(self.boot_image, iso_path=f'/{boot_iso_name}')
                iso.add_eltorito(f'/{boot_iso_name}', boot_load_size=4)

            self.log.emit("📂 Dosyalar taranıyor...")
            files_to_process = []
            for root, dirs, files in os.walk(self.source_folder):
                for file in files:
                    files_to_process.append(os.path.join(root, file))
            
            total_files = len(files_to_process)
            self.log.emit(f"📄 Toplam {total_files} dosya.")

            path_map = {self.source_folder: '/'}
            count = 0
            
            for current_path, directories, files in os.walk(self.source_folder):
                if not self.is_running: break
                current_iso_dir = path_map[current_path]
                
                for d in directories:
                    safe_dirname = self.get_safe_iso_name(d)
                    new_iso_dir = (current_iso_dir + '/' + safe_dirname).replace('//', '/')
                    
                    local_dir = os.path.join(current_path, d)
                    path_map[local_dir] = new_iso_dir
                    joliet_path = '/' + os.path.relpath(local_dir, self.source_folder).replace(os.sep, '/')
                    
                    try:
                        iso.add_directory(new_iso_dir, joliet_path=joliet_path, rr_name=d, udf_path=joliet_path)
                    except: pass

                for f in files:
                    if not self.is_running: break
                    local_file = os.path.join(current_path, f)
                    safe_filename = self.get_safe_iso_name(f)
                    iso_file = (current_iso_dir + '/' + safe_filename).replace('//', '/')
                    joliet_file = '/' + os.path.relpath(local_file, self.source_folder).replace(os.sep, '/')
                    
                    try:
                        iso.add_file(local_file, iso_path=iso_file, joliet_path=joliet_file, rr_name=f, udf_path=joliet_file)
                        if count % 20 == 0: self.log.emit(f"İşleniyor: {f}")
                    except Exception as e:
                        self.log.emit(f"HATA: {f} - {e}")
                    
                    count += 1
                    if total_files > 0: self.progress.emit(int((count/total_files)*90))

            if not self.is_running:
                iso.close()
                self.finished.emit(False, "İptal edildi.")
                return

            self.log.emit("💾 ISO yazılıyor...")
            self.progress.emit(95)
            iso.write(self.iso_path)
            iso.close()
            self.progress.emit(98)
            
            self.log.emit("🔐 Checksum (SHA256) hesaplanıyor...")
            checksum = calculate_checksum(self.iso_path)
            self.log.emit(f"SHA256: {checksum}")
            
            self.progress.emit(100)
            self.finished.emit(True, f"Başarılı!\nKayıt: {self.iso_path}\nSHA256: {checksum}")

        except Exception as e:
            msg = str(e)
            if "Input string too long" in msg: msg = "Dosya isimleri çok uzun! Kısaltıp tekrar deneyin."
            self.finished.emit(False, msg)

    def stop(self):
        self.is_running = False

# --- ANA PENCERE ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setFixedSize(720, 650)
        self.center_on_screen()

        self.icon_path = resource_path('assets/icon.png')
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
        
        self.init_menu()
        self.init_tray()
        self.source_folder = None
        self.worker = None
        self.is_processing = False
        self.init_ui()
        self.apply_styles()
        
        QTimer.singleShot(3000, self.baslangic_guncelleme_kontrolu)

    def init_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #2c3e50; color: white;")
        
        file_menu = menubar.addMenu("Dosya")
        act_quit = QAction("Çıkış", self)
        act_quit.triggered.connect(self.quit_app)
        file_menu.addAction(act_quit)
        
        tools_menu = menubar.addMenu("Araçlar")
        
        act_mount = QAction("ISO Bağla (Mount)", self)
        act_mount.triggered.connect(self.tool_mount_iso)
        tools_menu.addAction(act_mount)
        
        act_check = QAction("Checksum Hesapla", self)
        act_check.triggered.connect(self.tool_calculate_hash)
        tools_menu.addAction(act_check)
        
        # USB/DVD Yazdırma kaldırıldı

        help_menu = menubar.addMenu("Yardım")
        act_about = QAction("Hakkında", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title_lbl = QLabel(APP_NAME)
        title_lbl.setObjectName("title")
        ver_lbl = QLabel(APP_VERSION)
        ver_lbl.setObjectName("version")
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(ver_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.drop_area = QPushButton("Klasörü Buraya Sürükleyin\nveya Seçmek İçin Tıklayın")
        self.drop_area.setObjectName("dropArea")
        self.drop_area.setFixedHeight(100)
        self.drop_area.setAcceptDrops(True)
        self.drop_area.clicked.connect(self.select_folder)
        layout.addWidget(self.drop_area)

        self.path_lbl = QLabel("Henüz klasör seçilmedi")
        self.path_lbl.setObjectName("pathLabel")
        self.path_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.path_lbl)

        settings_frame = QFrame()
        settings_frame.setStyleSheet("background-color: #252e35; border-radius: 8px; padding: 5px;")
        sf_layout = QVBoxLayout(settings_frame)
        
        lbl_layout = QHBoxLayout()
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("ISO Etiketi (Otomatik)")
        lbl_layout.addWidget(QLabel("Etiket:"))
        lbl_layout.addWidget(self.label_input)
        sf_layout.addLayout(lbl_layout)
        
        self.chk_bootable = QCheckBox("Önyüklenebilir (Bootable) ISO Yap")
        self.chk_bootable.setStyleSheet("color: #ecf0f1; margin-top: 5px;")
        self.chk_bootable.toggled.connect(self.toggle_boot_options)
        sf_layout.addWidget(self.chk_bootable)
        
        self.boot_img_layout = QHBoxLayout()
        self.boot_img_input = QLineEdit()
        self.boot_img_input.setPlaceholderText("Boot İmajı Seç (efiboot.img vb.)")
        self.btn_browse_boot = QPushButton("...")
        self.btn_browse_boot.setFixedWidth(40)
        self.btn_browse_boot.clicked.connect(self.select_boot_image)
        
        self.boot_img_layout.addWidget(QLabel("Boot İmajı:"))
        self.boot_img_layout.addWidget(self.boot_img_input)
        self.boot_img_layout.addWidget(self.btn_browse_boot)
        
        self.boot_widget = QWidget()
        self.boot_widget.setLayout(self.boot_img_layout)
        self.boot_widget.setVisible(False)
        sf_layout.addWidget(self.boot_widget)
        
        layout.addWidget(settings_frame)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setObjectName("logBox")
        layout.addWidget(self.log_box)

        self.pbar = QProgressBar()
        self.pbar.setValue(0)
        self.pbar.setTextVisible(False)
        layout.addWidget(self.pbar)

        btn_layout = QHBoxLayout()
        self.action_btn = QPushButton("ISO OLUŞTUR")
        self.action_btn.setObjectName("createBtn")
        self.action_btn.setEnabled(False)
        self.action_btn.clicked.connect(self.toggle_process)
        btn_layout.addStretch()
        btn_layout.addWidget(self.action_btn)
        layout.addLayout(btn_layout)

        footer = QLabel(f"{APP_TITLE} | Linux System Tool")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #7f8c8d; font-size: 10px; margin-top: 5px;")
        layout.addWidget(footer)

    def toggle_boot_options(self, checked):
        self.boot_widget.setVisible(checked)

    def select_boot_image(self):
        f, _ = QFileDialog.getOpenFileName(self, "Boot İmajı Seç", "", "Image Files (*.img *.bin *.iso)")
        if f: self.boot_img_input.setText(f)

    def tool_calculate_hash(self):
        f, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Tüm Dosyalar (*.*)")
        if f:
            self.log_message(f"Hesaplanıyor: {f}")
            h = calculate_checksum(f, "sha256")
            self.log_message(f"SHA256: {h}")
            QMessageBox.information(self, "Checksum Sonucu", f"Dosya: {os.path.basename(f)}\n\nSHA256:\n{h}")

    def tool_mount_iso(self):
        f, _ = QFileDialog.getOpenFileName(self, "ISO Dosyası Seç", "", "ISO Files (*.iso)")
        if f:
            QMessageBox.information(self, "Mount İşlemi", 
                f"Bu işlem için yönetici yetkisi gerekir.\n\nTerminalde şu komut çalıştırılacak:\npkexec gnome-disk-image-mounter '{f}'")
            try:
                subprocess.Popen(["pkexec", "gnome-disk-image-mounter", f])
            except:
                QMessageBox.warning(self, "Hata", "Mount aracı bulunamadı (gnome-disk-image-mounter).")

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e272e; }
            QLabel { color: #d2dae2; font-size: 14px; }
            #title { font-size: 28px; font-weight: bold; color: #3498db; }
            #version { font-size: 12px; color: #f39c12; margin-top: 10px; margin-left: 5px; font-weight: bold; }
            #pathLabel { color: #ffdd59; font-style: italic; }
            QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; padding: 8px; border-radius: 4px; }
            QPushButton#dropArea { background-color: #2f3640; color: #ecf0f1; border: 2px dashed #3498db; border-radius: 10px; font-size: 16px; font-weight: bold; }
            QPushButton#dropArea:hover { background-color: #353b48; border-color: #54a0ff; }
            QTextEdit#logBox { background-color: #000; color: #00d2d3; border: 1px solid #34495e; font-family: monospace; font-size: 11px; }
            QProgressBar { border: 2px solid #2c3e50; border-radius: 5px; text-align: center; background-color: #2c3e50; height: 15px; }
            QProgressBar::chunk { background-color: #3498db; }
            QPushButton#createBtn { background-color: #27ae60; color: white; padding: 10px 40px; border: none; border-radius: 5px; font-weight: bold; font-size: 14px; }
            QPushButton#createBtn:disabled { background-color: #7f8c8d; }
            QPushButton#createBtn:hover { background-color: #2ecc71; }
        """)

    def show_about(self):
        dialog = HakkindaDialog(self)
        dialog.exec()

    def baslangic_guncelleme_kontrolu(self):
        self.updater = GuncellemeKontrolcusu(APP_VERSION)
        self.updater.guncelleme_var_sinyali.connect(self.show_update_dialog)
        self.updater.start()

    def show_update_dialog(self, yeni_surum, notlar, link):
        msg = QMessageBox(self)
        msg.setWindowTitle("Güncelleme Mevcut")
        msg.setText(f"<b>Yeni Sürüm: {yeni_surum}</b><br><br>Yenilikler:<br>{notlar}")
        msg.setInformativeText("İndirmek ister misiniz?")
        msg.setIcon(QMessageBox.Icon.Information)
        btn_indir = msg.addButton("İndir", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("İptal", QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        if msg.clickedButton() == btn_indir:
            self.baslat_guncelleme_terminali(link)

    def baslat_guncelleme_terminali(self, link):
        if link:
            dosya_adi = link.split("/")[-1]
            komut = f"""cd /tmp && wget -q --show-progress -O {dosya_adi} {link} && sudo dpkg -i {dosya_adi} && read -p 'Bitti. Enter...' && exit"""
            try: subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c \"{komut}\""]) 
            except: webbrowser.open(link)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and os.path.isdir(files[0]): self.set_folder(files[0])

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(APP_NAME, "Arkaplanda çalışıyor.", QSystemTrayIcon.MessageIcon.Information, 1000)
            event.ignore()
        else: event.accept()

    def show_window(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()

    def quit_app(self):
        if self.is_processing:
             reply = QMessageBox.question(self, 'Çıkış', "İşlem sürüyor. Çıkmak istiyor musunuz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
             if reply == QMessageBox.StandardButton.No: return
        QApplication.quit()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Kaynak Klasör Seç")
        if folder: self.set_folder(folder)

    def set_folder(self, path):
        if self.is_processing: return
        self.source_folder = path
        self.path_lbl.setText(path)
        self.action_btn.setEnabled(True)
        safe_label = os.path.basename(path).upper().replace(" ", "_")
        self.label_input.setText(safe_label)
        self.log_message(f"Hedef: {path}")

    def log_message(self, msg):
        self.log_box.append(f"> {msg}")
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def center_on_screen(self):
        qt_rectangle = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(self.icon_path): self.tray_icon.setIcon(QIcon(self.icon_path))
        tray_menu = QMenu()
        tray_menu.addAction("Göster", self.show_window)
        tray_menu.addAction("Çıkış", self.quit_app)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def toggle_process(self):
        if not self.is_processing:
            if not self.source_folder: return
            default_name = f"{self.label_input.text()}.iso" if self.label_input.text() else "backup.iso"
            save_path, _ = QFileDialog.getSaveFileName(self, "ISO Kaydet", os.path.join(os.path.expanduser("~"), default_name), "ISO Dosyası (*.iso)")
            if not save_path: return
            if not save_path.endswith('.iso'): save_path += '.iso'
            
            self.start_processing_ui()
            vol_label = self.label_input.text() or "ISOCU_DISK"
            boot_img = self.boot_img_input.text() if self.chk_bootable.isChecked() else None
            
            self.worker = IsoWorker(self.source_folder, save_path, vol_label, boot_img)
            self.worker.progress.connect(self.pbar.setValue)
            self.worker.log.connect(self.log_message)
            self.worker.finished.connect(self.process_finished)
            self.worker.start()
        else:
            if self.worker:
                self.worker.stop()
                self.log_message("⚠️ İptal ediliyor...")
                self.action_btn.setEnabled(False)

    def start_processing_ui(self):
        self.is_processing = True
        self.drop_area.setEnabled(False)
        self.pbar.setValue(0)
        self.action_btn.setText("İPTAL ET")
        self.action_btn.setStyleSheet("background-color: #c0392b; color: white; padding: 10px 40px; border-radius: 5px; font-weight: bold;")
        self.log_message(f"--- {APP_NAME} İşleme Başlıyor ---")

    def process_finished(self, success, message):
        self.is_processing = False
        self.drop_area.setEnabled(True)
        self.action_btn.setEnabled(True)
        self.action_btn.setText("ISO OLUŞTUR")
        self.action_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px 40px; border-radius: 5px; font-weight: bold;")

        if success:
            self.tray_icon.showMessage(APP_NAME, "İşlem tamamlandı!", QSystemTrayIcon.MessageIcon.Information, 3000)
            if not self.isHidden(): QMessageBox.information(self, "Başarılı", message)
            self.log_message("--- İŞLEM TAMAMLANDI ---")
        else:
            self.tray_icon.showMessage(APP_NAME, "Hata", "İşlem başarısız.", QSystemTrayIcon.MessageIcon.Warning, 3000)
            self.log_message(f"DURUM: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    socket = QLocalSocket()
    socket.connectToServer(APP_ID)
    if socket.waitForConnected(500):
        socket.write(b"SHOW_WINDOW") 
        socket.waitForBytesWritten(1000)
        sys.exit(0)
    else:
        local_server = QLocalServer()
        local_server.removeServer(APP_ID)
        local_server.listen(APP_ID)

    app.setDesktopFileName("isocu.desktop") 
    icon_path = resource_path('assets/icon.png')
    if os.path.exists(icon_path): app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.setAcceptDrops(True)
    local_server.newConnection.connect(lambda: window.show_window())
    window.show()
    app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec())