****12.10.25'te yaptığım Değişiklikler****
-Veritabanı gitmemek üzere geri getirildi(inşallah)
-Veritabanının doğru çalıştığını anlamak üzerine denemeler yapılıyor, şu an menü tam olarak geliyor mu ona bakıyorum eğer geliyorsa masa isimlerinde olan değişiklikler yapılacak bu değişikliğin olması için de table_number yazan tüm dosya içerikleri table.name olarak düzenlenecek. Şu an masa adlarının görünmeme sebebi bu.
-table.py dosyası yeniden düzenlendi.
-tüm dosyalardaki table_number kısımları düzeltildi artık masa seçimi doğru bir şekilde çalışıyor. 
- masa seçimi ve siparişi onaylama kısmı tek sayfada birleştirildi.
-Admin panelinde bulunan ödeme yönetimi ve raporlar kısmı hariç tüm sayfaların arayüzleri değiştirildi.
-Şuanlık bu kadar hepimiz birlikte oturup neyin ne olmasına karar vermemiz gerekiyor ne çıkarılacak ne kalacak gibi
bu kararı verdikten sonra tam değişiklikler yapılacak
-Docker ile çalışmayı duruma göre iptal edebiliriz diye düşünüyorum ama ilkay hocayla konuştuktan sonra buna karar verelim bence çünkü dockerın çalışma mantığını anlamak hepimiz için iyi
- Bazı yemeklerin görselleri değiştirlmiş figmadan yeni görseller alınacak

******** 17.11.25 **********
- Yeni ürün ekle kısmına dosya ekleme kısmı eklendi
- Admin girişi sağ üst köşeye taşındı
- Giriş yapan adminin ismi hatalı olarak alınıyordu düzeltildi ve admin profil düzenle sayfası düzeltildi
- yemekler kısmında ürün görselleri güncellendi
- şöyle bir sorunumuz var:
 Bu Projede:
Veritabanı: SQLite (restaurant.db)
ORM: SQLAlchemy
SQL: Otomatik oluşturuluyor, yazmana gerek yok
Modeller: models klasöründe Python sınıfları
Sonuç: SQLAlchemy sayesinde SQL yazmadan Python ile veritabanı yönetiyorsun! 🚀
bizim aslında sql kodlarımız yok bunu kesinlikle hocaya sormalıyız!!!!
- kevser abla ben views klasörünü kopyasında sildim bir şey değişmedi proje çalıştı ama yine de sen de bi dene öyle kaldıralım
