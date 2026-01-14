import sys
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QSlider, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QTimer

# ═══════════════════════════════════════════════════════════════════════════
# DEPHAZE KERNEL v1.0  
# ═══════════════════════════════════════════════════════════════════════════

def dephaze_v10_kernel(signal, gain_factor):
    PHI3 = 4.23606797749979
    ANCHOR = 1e-55 
    IMAGO_Z = PHI3 * ANCHOR 

    pole = np.sign(signal)
    abs_s = np.abs(signal)

    x = abs_s * ANCHOR
    y = np.power(abs_s, 2) * ANCHOR
    z = IMAGO_Z

    R = np.sqrt(np.power(x, 2) + np.power(y, 2) + np.power(z, 2))
    d = np.power(
        np.power(np.abs(x), PHI3) + 
        np.power(np.abs(y), PHI3) + 
        np.power(np.abs(z), PHI3),
        1.0 / PHI3
    )

    Xi = R / np.maximum(d, 1e-250)
    vortex = Xi * PHI3
    return pole * abs_s * vortex * gain_factor, Xi

# ═══════════════════════════════════════════════════════════════════════════
# AUDIO ENGINE  
# ═══════════════════════════════════════════════════════════════════════════

class DephazeEngine:
    def __init__(self):
        self.gain_factor = 0.40
        self.stereo_spread = 1.0  # Új paraméter
        self.is_active = False
        self.last_xi = 1.0
        self.stream = None
        self.in_buf = deque(maxlen=2000)
        self.out_buf = deque(maxlen=2000)
        self.xi_buf = deque(maxlen=2000)

    def audio_callback(self, indata, outdata, frames, time, status):
        if not self.is_active:
            outdata.fill(0); return
            
        # Bal és Jobb csatorna különválasztása
        l_in = indata[:, 0].astype(np.float64)
        r_in = indata[:, 1].astype(np.float64)
        
        # Mindkét csatorna átvezetése a Lamé-kernelen (Axiom 1 & 2)
        l_out, l_xi = dephaze_v10_kernel(l_in, self.gain_factor)
        r_out, r_xi = dephaze_v10_kernel(r_in, self.gain_factor)
        
        # --- STEREO SPREAD (M/S Topológiai tágítás) ---
        if abs(self.stereo_spread - 1.0) > 0.001:
            mid = (l_out + r_out) * 0.5
            side = (l_out - r_out) * 0.5
            l_out = mid + (side * self.stereo_spread)
            r_out = mid - (side * self.stereo_spread)
        
        self.in_buf.extend(l_in)
        self.out_buf.extend(l_out)
        self.xi_buf.extend(l_xi)
        self.last_xi = np.mean(l_xi)
        
        outdata[:, 0] = l_out.astype(np.float32)
        outdata[:, 1] = r_out.astype(np.float32)

    def start(self, in_id, out_id):
        if self.is_active: return
        try:
            self.stream = sd.Stream(device=(in_id, out_id), channels=2, samplerate=48000, 
                                   callback=self.audio_callback, blocksize=256)
            self.stream.start()
            self.is_active = True
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def stop(self):
        self.is_active = False
        if self.stream:
            try: self.stream.stop(); self.stream.close()
            except: pass
            self.stream = None
        sd.stop()
        self.save_diag()

    def save_diag(self):
        if not self.in_buf: return
        plt.figure(figsize=(10, 6), facecolor='black')
        plt.subplot(2, 1, 1, facecolor='black')
        plt.plot(list(self.in_buf), color='gray', alpha=0.5)
        plt.plot(list(self.out_buf), color='cyan', alpha=0.8)
        plt.subplot(2, 1, 2, facecolor='black')
        plt.plot(list(self.xi_buf), color='#B8860B')
        plt.tight_layout(); plt.savefig("dephaze_v93_plot.png"); plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# GUI  
# ═══════════════════════════════════════════════════════════════════════════

class DephazeUI(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("DEPHAZE v10 | Hardware Clean")
        self.setFixedSize(450, 580)
        self.setStyleSheet("background-color: #000; color: #0ff; font-family: monospace;")
        
        layout = QVBoxLayout()
        central = QWidget(); central.setLayout(layout); self.setCentralWidget(central)
        
        header = QLabel("DephazEAudi0")
        header.setStyleSheet("font-size: 28px; font-weight: light; color: #0ff; margin: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(header)
        
        self.monitor = QLabel("MODULATION: 1.0000")
        self.monitor.setStyleSheet("background: #050510; padding: 20px; color: #B8860B; border: 2px solid #B8860B; border-radius: 12px; font-size: 18px;")
        self.monitor.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.monitor)

        layout.addSpacing(10)
        
        # --- ESZKÖZVÁLASZTÓK ---
        self.l_in_title = QLabel("LIVE INPUT DEVICE:")
        self.l_in_title.setStyleSheet("color: #B8860B; font-weight: light; margin-top: 5px;")
        layout.addWidget(self.l_in_title)
        
        self.in_combo = QComboBox()
        self.in_combo.setStyleSheet("background-color: #050510; color: #B8860B; border: 1px solid #B8860B; padding: 3px;")
        layout.addWidget(self.in_combo)
        
        self.l_out_title = QLabel("LIVE OUTPUT DEVICE:")
        self.l_out_title.setStyleSheet("color: #B8860B; font-weight: light; margin-top: 5px;")
        layout.addWidget(self.l_out_title)
        
        self.out_combo = QComboBox()
        self.out_combo.setStyleSheet("background-color: #050510; color: #B8860B; border: 1px solid #B8860B; padding: 3px;")
        layout.addWidget(self.out_combo)
        
        self.populate_clean_devices()

        layout.addSpacing(15)
        
        # --- GAIN  ---
        layout.addWidget(QLabel("GAIN"))
        self.s_drive = QSlider(Qt.Orientation.Horizontal)
        self.s_drive.setRange(0, 100); self.s_drive.setValue(40)
        self.s_drive.valueChanged.connect(self.upd_gain); layout.addWidget(self.s_drive)
        self.l_drive = QLabel("0.40"); self.l_drive.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.l_drive)

        layout.addSpacing(10)

        # --- STEREO SPREAD  ---
        layout.addWidget(QLabel("STEREO SPREAD"))
        self.s_spread = QSlider(Qt.Orientation.Horizontal)
        self.s_spread.setRange(0, 300); self.s_spread.setValue(100)
        self.s_spread.valueChanged.connect(self.upd_spread); layout.addWidget(self.s_spread)
        self.l_spread = QLabel("1.00"); self.l_spread.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.l_spread)

        layout.addSpacing(15)

        self.btn = QPushButton("ENTER")
        self.btn.setMinimumHeight(80)
        self.btn.setFixedWidth(200)
        self.btn.clicked.connect(self.toggle)
        self.set_style(False)
        layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        copy = QLabel("Copyright 2026 Angus Dewer 10.5281/zenodo.18244991")
        copy.setStyleSheet("color: #444; font-size: 10px; margin-top: 5px;")
        copy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copy)
        
        self.timer = QTimer(); self.timer.timeout.connect(self.refresh); self.timer.start(50)

    def populate_clean_devices(self):
        devices = sd.query_devices()
        in_names = set(); out_names = set()
        for i, d in enumerate(devices):
            name = d['name']
            if d['max_input_channels'] > 0 and name not in in_names:
                try:
                    sd.check_input_settings(device=i, samplerate=48000)
                    self.in_combo.addItem(name, i); in_names.add(name)
                except: continue
            if d['max_output_channels'] > 0 and name not in out_names:
                try:
                    sd.check_output_settings(device=i, samplerate=48000)
                    self.out_combo.addItem(name, i); out_names.add(name)
                except: continue

    def upd_gain(self, v):
        d = v / 100.0; self.engine.gain_factor = d; self.l_drive.setText(f"{d:.2f}")

    def upd_spread(self, v):
        s = v / 100.0; self.engine.stereo_spread = s; self.l_spread.setText(f"{s:.2f}")

    def refresh(self):
        if self.engine.is_active: self.monitor.setText(f"MODULATION: {self.engine.last_xi:.6f}")

    def toggle(self):
        if self.engine.is_active:
            self.engine.stop(); self.set_style(False)
            self.in_combo.setEnabled(True); self.out_combo.setEnabled(True)
        else:
            in_id = self.in_combo.currentData()
            out_id = self.out_combo.currentData()
            if self.engine.start(in_id, out_id):
                self.set_style(True)
                self.in_combo.setEnabled(False); self.out_combo.setEnabled(False)
            else:
                QMessageBox.critical(self, "Device Error", "Selected hardware is busy or invalid at 48kHz.")

    def set_style(self, run):
        if run:
            self.btn.setText("STOP")
            self.btn.setStyleSheet("background: #300; color: #B8860B; border: 3px solid #B8860B; font-weight: light; font-size: 22px; border-radius: 15px;")
        else:
            self.btn.setText("ENTER")
            self.btn.setStyleSheet("background: #003; color: #0ff; border: 3px solid #B8860B; font-weight: light; font-size: 22px; border-radius: 15px;")

if __name__ == "__main__":
    app = QApplication(sys.argv); engine = DephazeEngine(); gui = DephazeUI(engine); gui.show(); sys.exit(app.exec())