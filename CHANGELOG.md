# 📦 CHANGELOG

**Proje:** SoundFrame
**Yazar:** Emir Topay  
**Sürüm:** v1.2-Release  
**Tarih:** 2025-06-13

---

## 🔄 Değişiklik Özeti

Bu sürüm, temel işlevselliğe sahip sade ilk versiyondan daha modüler, kullanıcı dostu ve genişletilebilir bir yapıya sahip gelişmiş versiyona geçişi temsil eder.

---

## 🚀 Yeni Eklenen Özellikler (Toplam 6)

### ✅ 1. Çoklu OLED Ekran Desteği
- `userConfig.h` üzerinden SH1106 ve SSD1306 desteği tanımlanabilir hale getirildi.
- Tek satır değişiklikle farklı ekranlarla uyumluluk sağlandı.
```cpp
#if defined(USE_SH1106)
...
#elif defined(USE_SSD1306)
...
#endif
```
### ✅ 2. Logo / Bitmap Gösterimi
Proje başlangıcında startLogo ve waitLogo bitmap'leri gösteriliyor.

Görsel karşılık ve daha profesyonel bir açılış animasyonu sunuyor.
```
showBitmap(startLogo);
delay(2000);
showBitmap(waitLogo);
```
### ✅ 3. Seri Bağlantı Bekleme Ekranı
Bağlantı sağlanmadan veri alınmaz, bunun yerine bekleme ekranı gösterilir.

Kullanıcıya "bağlantı hazır değil" durumu görsel olarak iletilir.

```
if (!connected) {
  if (Serial.available()) {
    connected = true;
    ...
```
### ✅ 4. userConfig.h Desteği
I2C pinleri (I2C_SDA, I2C_SCL), OLED adresi ve bant sayısı gibi ayarlar dışarıdan tanımlanabilir hale getirildi.

```
#include "userConfig.h"
```
Daha kolay yapılandırma ve çoklu platform desteği sağlandı.

### ✅ 5. Ortak Renk Tanımı (Abstraction)
COLOR_WHITE makrosu ile SH1106 ve SSD1306 için renk bağımsız kod kullanımı.

```
#define COLOR_WHITE SH110X_WHITE // veya WHITE
```
### ✅ 6. Fonksiyonlaştırılmış Bitmap Gösterimi
```
showBitmap() fonksiyonu eklendi.
```
Logo gibi bitmap'lerin tekrar tekrar kolayca gösterilmesi sağlandı.

```
void showBitmap(const unsigned char *bitmap) {
  ...
}
```
##📌 Notlar
Kod, ileride dil desteği, tema seçimi veya farklı giriş türlerine (mikrofon, internet) uyarlanabilir.

Yapı modüler hale getirildiği için katkı yapmak isteyen geliştiricilere açıktır.

🔢 Sürüm Geçmişi
Sürüm	Tarih	Açıklama
v1.0	2023-5-26	İlk sade sürüm
v1.2	2025-06-13	Gelişmiş, modüler yapı

