import tkinter as tk
from tkinter import ttk, Scale
import serial.tools.list_ports
import pyaudio
import numpy as np
import threading
import time
import math

CHUNK = 2048  # Daha büyük chunk daha iyi frekans çözünürlüğü
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
ser = None
stream = None

# EQ ayarları için global değişkenler
global_gain = 1.0
bass_boost = 0.3
mid_boost = 1.4
treble_boost = 5.0

root = tk.Tk()
root.title("ESP32 Ses Görselleştirici")
root.geometry("500x700")

# Ana frame
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# COM Portu seçim bölümü
com_frame = ttk.LabelFrame(main_frame, text="Seri Port Ayarları", padding=10)
com_frame.pack(fill=tk.X, pady=5)

com_port_label = ttk.Label(com_frame, text="COM Portu Seçin:")
com_port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

com_port_combobox = ttk.Combobox(com_frame, state="readonly", width=30)
com_port_combobox.grid(row=0, column=1, padx=5, pady=5)

def refresh_com_ports():
    ports = serial.tools.list_ports.comports()
    com_port_combobox['values'] = [port.device for port in ports]
    if ports:
        com_port_combobox.current(0)

refresh_button = ttk.Button(com_frame, text="Yenile", command=refresh_com_ports)
refresh_button.grid(row=0, column=2, padx=5, pady=5)

# Ses Girişi seçim bölümü
input_frame = ttk.LabelFrame(main_frame, text="Ses Giriş Ayarları", padding=10)
input_frame.pack(fill=tk.X, pady=5)

input_device_label = ttk.Label(input_frame, text="Ses Giriş Cihazı Seçin:")
input_device_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

input_device_combobox = ttk.Combobox(input_frame, state="readonly", width=30)
input_device_combobox.grid(row=0, column=1, padx=5, pady=5)

def refresh_input_devices():
    input_devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_devices.append(f"{device_info['index']}: {device_info['name']}")
    input_device_combobox['values'] = input_devices
    if input_devices:
        input_device_combobox.current(0)

refresh_input_button = ttk.Button(input_frame, text="Yenile", command=refresh_input_devices)
refresh_input_button.grid(row=0, column=2, padx=5, pady=5)

# EQ Kontrolleri
eq_frame = ttk.LabelFrame(main_frame, text="Ekolayzır Ayarları", padding=10)
eq_frame.pack(fill=tk.X, pady=10)

def create_eq_slider(frame, label, from_, to, row):
    ttk.Label(frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
    scale = Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, resolution=0.1, length=300)
    scale.set(1.0)
    scale.grid(row=row, column=1, padx=5, pady=5)
    return scale

gain_scale = create_eq_slider(eq_frame, "Gain (Kazanç):", 0.1, 5.0, 0)  # Maksimum kazanç artırıldı
bass_scale = create_eq_slider(eq_frame, "Bas (Düşük Frekans):", 0.1, 5.0, 1)
mid_scale = create_eq_slider(eq_frame, "Mid (Orta Frekans):", 0.1, 5.0, 2)
treble_scale = create_eq_slider(eq_frame, "Tiz (Yüksek Frekans):", 0.1, 5.0, 3)

# Dinamik Aralık Ayarları
dynamic_frame = ttk.LabelFrame(main_frame, text="Dinamik Aralık Ayarları", padding=10)
dynamic_frame.pack(fill=tk.X, pady=10)

min_level_label = ttk.Label(dynamic_frame, text="Min. Seviye:")
min_level_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
min_level_scale = Scale(dynamic_frame, from_=0, to=50, orient=tk.HORIZONTAL, length=300)
min_level_scale.set(10)  # Varsayılan min seviye
min_level_scale.grid(row=0, column=1, padx=5, pady=5)

sensitivity_label = ttk.Label(dynamic_frame, text="Hassasiyet:")
sensitivity_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
sensitivity_scale = Scale(dynamic_frame, from_=0.5, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, length=300)
sensitivity_scale.set(1.5)  # Varsayılan hassasiyet
sensitivity_scale.grid(row=1, column=1, padx=5, pady=5)

# Butonlar
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

def connect_to_esp32():
    global ser
    selected_port = com_port_combobox.get()
    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(selected_port, 115200, timeout=1)
        status_label.config(text=f"Bağlandı: {selected_port}", fg="green")
    except Exception as e:
        status_label.config(text=f"Hata: {str(e)}", fg="red")

connect_button = ttk.Button(button_frame, text="ESP32'ye Bağlan", command=connect_to_esp32)
connect_button.pack(side=tk.LEFT, padx=5)

def select_input_device():
    global stream
    if stream:
        stream.stop_stream()
        stream.close()
    selected_device = input_device_combobox.get()
    if selected_device:
        device_index = int(selected_device.split(":")[0])
        try:
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=CHUNK)
            status_label.config(text=f"Ses cihazı seçildi: {selected_device}", fg="blue")
        except Exception as e:
            status_label.config(text=f"Hata: {str(e)}", fg="red")

select_device_button = ttk.Button(button_frame, text="Ses Cihazını Seç", command=select_input_device)
select_device_button.pack(side=tk.LEFT, padx=5)

def apply_eq_settings():
    global global_gain, bass_boost, mid_boost, treble_boost
    global_gain = gain_scale.get()
    bass_boost = bass_scale.get()
    mid_boost = mid_scale.get()
    treble_boost = treble_scale.get()
    status_label.config(text="EQ ayarları uygulandı", fg="purple")

apply_eq_button = ttk.Button(button_frame, text="EQ Ayarlarını Uygula", command=apply_eq_settings)
apply_eq_button.pack(side=tk.LEFT, padx=5)

# Durum göstergesi
status_label = tk.Label(main_frame, text="Bağlantı bekleniyor...", fg="black", font=("Arial", 10))
status_label.pack(pady=10)

# Performans göstergesi
perf_label = tk.Label(main_frame, text="FPS: 0 | Max Band: 0", fg="gray", font=("Arial", 8))
perf_label.pack(pady=5)

# Dinamik aralık için değişkenler
dynamic_min = 10
dynamic_max = 0
dynamic_decay = 0.95  # Dinamik maksimumun yavaşça azalması için

def process_audio():
    global dynamic_min, dynamic_max
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        if ser and ser.is_open and stream:
            try:
                # Kaydırıcılardan güncel ayarları al
                gain = gain_scale.get()
                bass = bass_scale.get()
                mid = mid_scale.get()
                treble = treble_scale.get()
                min_level = min_level_scale.get()
                sensitivity = sensitivity_scale.get()
                
                # Ses verisini oku
                data = stream.read(CHUNK, exception_on_overflow=False)
                data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                
                # Gain uygula
                data *= gain
                
                # Pencereleme fonksiyonu uygula (sızıntıyı azalt)
                window = np.hanning(len(data))
                data = data * window
                
                # FFT hesapla
                fft_data = np.fft.rfft(data)
                fft_magnitude = np.abs(fft_data)
                
                # Frekans bandları için EQ uygula
                freqs = np.fft.rfftfreq(len(data), 1.0/RATE)
                
                # EQ uygulama
                for i, freq in enumerate(freqs):
                    if freq < 250:  # Bas frekansları
                        fft_magnitude[i] *= bass
                    elif freq < 4000:  # Mid frekansları
                        fft_magnitude[i] *= mid
                    else:  # Tiz frekansları
                        fft_magnitude[i] *= treble
                
                # Bandlara ayır (logaritmik olarak)
                bands = []
                band_edges = np.logspace(np.log10(20), np.log10(20000), 33)  # 32 bant için 33 kenar
                for i in range(32):
                    start_freq = band_edges[i]
                    end_freq = band_edges[i+1]
                    indices = np.where((freqs >= start_freq) & (freqs < end_freq))[0]
                    
                    if len(indices) > 0:
                        band_value = np.mean(fft_magnitude[indices])
                    else:
                        band_value = 0
                    
                    bands.append(band_value)
                
                band_values = np.array(bands)
                
                # Dinamik aralığı güncelle
                current_max = np.max(band_values)
                if current_max > dynamic_max:
                    dynamic_max = current_max
                else:
                    dynamic_max = dynamic_max * dynamic_decay + current_max * (1 - dynamic_decay)
                
                # Normalize et (dinamik aralık kullanarak)
                band_values = np.clip(band_values, min_level, dynamic_max)
                band_values = (band_values - min_level) / (dynamic_max - min_level) * 100 * sensitivity
                band_values = np.clip(band_values, 0, 100).astype(int)
                
                # Seri port üzerinden gönder
                ser.write(f"bars,{','.join(map(str, band_values))}\n".encode())
                
                # FPS hesapla
                frame_count += 1
                if time.time() - start_time > 1.0:
                    fps = frame_count / (time.time() - start_time)
                    current_max_val = np.max(band_values)
                    perf_label.config(text=f"FPS: {fps:.1f} | Max Band: {current_max_val}")
                    frame_count = 0
                    start_time = time.time()
                    
            except Exception as e:
                print(f"Hata: {str(e)}")
                status_label.config(text=f"Ses işleme hatası: {str(e)}", fg="red")
                time.sleep(1)  # Hata durumunda CPU'yu kilitlememek için
        else:
            time.sleep(0.1)  # CPU kullanımını azalt

# Başlangıçta portları yenile
refresh_com_ports()
refresh_input_devices()

# Ses işleme thread'ini başlat
audio_thread = threading.Thread(target=process_audio, daemon=True)
audio_thread.start()

root.mainloop()