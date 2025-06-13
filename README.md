# SoundFrame

Bu proje, ESP32 ve SH1106 OLED ekran kullanarak gerçek zamanlı ses frekans spektrumunu görselleştiren bir sistemdir. Python uygulaması üzerinden mikrofon verisi alınır, FFT ile frekans analiz edilir, ekolayzır ile işlenir ve seri port üzerinden ESP32'ye gönderilir. ESP32 ise bu verileri OLED ekranda çubuk grafik olarak gösterir.

---

## Özellikler

- 32 bantlı FFT spektrum analizi  
- Python tarafında gerçek zamanlı ses yakalama ve FFT işleme  
- Bass, Mid, Treble ve genel gain için ayarlanabilir ekolayzır  
- Dinamik aralık ve hassasiyet kontrolü  
- SH1106 128x64 OLED ekran üzerinde görsel spektrum  
- Seri port üzerinden hızlı veri iletimi

---

## Gereksinimler

- Donanım:  
  - ESP32 (örneğin ESP32 LOLİN32 lite)  
  - SH1106 128x64 OLED ekran (I2C)  
- Yazılım:  
  - Arduino IDE ve `Adafruit_SH110X` kütüphanesi  
  - Python 3  
  - Python kütüphaneleri: `pyaudio`, `numpy`, `pyserial`, `tkinter`

---

## Kurulum ve Kullanım

1. Arduino kodunu ESP32'ye yükleyin. OLED ekran bağlantılarını doğru yapın (örneğin SDA=22, SCL=19).  
2. Python ortamını hazırlayın:  
   ```bash
   pip install pyaudio numpy pyserial
3.Python uygulamasını çalıştırın:python main.py
4.Seri port ve ses giriş cihazınızı seçin, EQ ayarlarını yapın ve ESP32'ye bağlanın.
---

## Lisans
MIT Lisansı altında lisanslanmıştır.
Detaylar için LICENSE dosyasına bakın

# İletişim
Herhangi bir sorun ya da öneri için [emir.topay2025@gmail.com] adresine ulaşabilirsiniz.
