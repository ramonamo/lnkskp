# 🔗 LinkGeç - URL Kısaltma Servisi

Flask tabanlı, reklamla para kazanan URL kısaltma servisi. Linkvertise benzeri özellikler sunar.

## 🚀 Özellikler

- ✅ **Hızlı URL Kısaltma**: Anında link kısaltma
- ✅ **3 Adımlı Reklam Sistemi**: Her adımda 15 saniye bekleme + reklam
- ✅ **Admin Panel**: Link yönetimi ve istatistikler
- ✅ **Ziyaret Takibi**: IP bazlı günlük ziyaret kontrolü
- ✅ **A-Ads Entegrasyonu**: Hazır reklam sistemi
- ✅ **Güvenlik**: Bypass koruması, rate limiting, bot koruması
- ✅ **Mobil Uyumlu**: Responsive tasarım

## 📦 Kurulum

### Gereksinimler
```bash
pip install Flask Flask-CORS validators
```

### Çalıştırma
```bash
python app.py
```

Uygulama `http://localhost:5001` adresinde çalışacak.

## 🔧 Kullanım

### Ana Sayfa
- **URL**: `http://localhost:5001`
- URL kısaltma formu
- Anında kısa link oluşturma

### Admin Panel
- **URL**: `http://localhost:5001/admin`
- **Kullanıcı**: `admin`
- **Şifre**: `admin123`

### Özellikler
- Link yönetimi (aktif/pasif, silme)
- Detaylı ziyaret istatistikleri
- Gerçek zamanlı veriler

## 💰 Reklam Sistemi

### A-Ads Entegrasyonu
Projede A-Ads (data-aa='2406589') reklamları entegre edilmiştir:
- Ana sayfada banner reklamı
- Her yönlendirme adımında reklam
- CPM optimizasyonu için 3 adımlı sistem

### Reklam Değiştirme
`app.py` dosyasında A-Ads iframe kodlarını kendi reklam kodunuzla değiştirin:
```html
<iframe data-aa='YOUR_AD_ID' src='//acceptable.a-ads.com/YOUR_AD_ID' ...></iframe>
```

## 📁 Proje Yapısı

```
📁 link-shortener/
├── 📄 app.py              # Ana Flask uygulaması (tüm kod burada)
├── 📄 requirements.txt    # Python dependencies
├── 📄 .gitignore         # Git ignore kuralları
├── 📄 README.md          # Bu dosya
└── 📁 data/              # Otomatik oluşur
    ├── 📁 links/         # Link dosyaları (JSON)
    ├── 📁 visits/        # Ziyaret kayıtları
    ├── 📄 admin.json     # Admin bilgileri
    ├── 📄 ads.json       # Reklam konfigürasyonları
    └── 📄 stats.json     # İstatistikler
```

## 🔒 Güvenlik Özellikleri

- **Rate Limiting**: Dakikada 5 link kısaltma limiti
- **Spam Koruması**: Saatte 10 link limiti
- **Bot Koruması**: User-Agent kontrolü
- **URL Validation**: Güvenli URL kontrolleri
- **Bypass Koruması**: Session, IP, süre kontrolleri
- **Sıralı Adım Kontrolü**: Adım atlama engeli

## 🎯 Yönlendirme Sistemi

1. **Adım 1**: İlk reklam ve güvenlik kontrolü (15s)
2. **Adım 2**: İkinci reklam ve doğrulama (15s)  
3. **Adım 3**: Son reklam ve kontrol (15s)
4. **Yönlendirme**: Hedef URL'ye otomatik yönlendirme

## 📊 İstatistikler

- Toplam link sayısı
- Aktif link sayısı
- Toplam tıklama sayısı
- Toplam ziyaret sayısı
- IP bazlı detaylı ziyaret takibi

## 🌐 Deployment

### Localhost
```bash
python app.py
```

### Production
- Heroku, DigitalOcean, AWS gibi platformlarda çalışabilir
- `requirements.txt` ile dependencies otomatik yüklenir
- Environment variables için `.env` dosyası kullanılabilir

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 💡 İpuçları

- Admin panelinde tüm linklerinizi yönetebilirsiniz
- Ziyaret detaylarını görmek için ziyaret sayısına tıklayın
- Reklam kodlarını değiştirmeyi unutmayın
- Production'da `debug=False` yapın

---

⭐ **Beğendiyseniz yıldız vermeyi unutmayın!**
