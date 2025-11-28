08.10.2025 Tarihinde Yaptığım Değişiklikler:
- Login telefon yerine e-mail girişine çevirildi. Database e-mail olarak ayarlandı
- Profil düzenleme kısmı geldi.
- Docker olmayanlar için init_db butonuna varsayılan database eklendi. Profilim kısmında.
- Sepete eklenen ürün için sepete eklend pop-up eklendi.
- Masaların doluluk kontrolü çalışmıyordu. Sepete ekleme durumuna göre masanın dolduğu ve ödeme durumunda masanın boşaldığı kontroller eklendi.
- Admin masaya ürün ekleyebilir duruma geldi.
- Admin sipariş durumunu güncelleyebiliyor.
- Renkler her pcde görülecek şekilde ayarlandı.
- Ürün eklerken yeni sipariş oluşturuyordu aynı masa için. bunu düzelttim artık ürün eklerken mevcut masaya ekliyor.
ŞUANLIK BUNLARI HATIRLIYORUM ABLA DAHA DEĞİŞİKLİK YAPMADIM SANKİ AMA ÇOK UYKUM GELDİĞİ İÇİN UNUTMUŞ OLABİLİRİM 6 SAATTİR BUNA BAKIYORUM HADİ ÖPTÜMMM

****09.10.25'te yaptığım Değişiklikler****
- Müşteri ve admin görünümünden çıkışta ana ekran bizim tasarladığımız ekrana sabitlendi.
- Menü ekranındaki masa seçim fonksiyonu kaldırıldı
- Arka plan görünümü menü ekranına eklendi.
- user_controller.py: Sepet -> sipariş akışını yeniden kurguladık; 
masa seçimi POST’a taşındı, 
geçmiş sipariş listelemesi tüm durumları kapsıyor, 
dashboard/menu yalnızca pending sepetleri aktif sayıyor.
- table.py: Masalara ait aktif sipariş arama ve toplam tutar hesapları Order tablosu üzerinden, tamamlanmış ama ödenmemiş siparişleri de kapsayacak şekilde güncellendi.
- utils/datetime_utils.py + app.py: Europe/Istanbul saat dilimi desteği eklendi; yeni datetime_tr filtresi tüm arayüzlerde kullanılıyor. templates ve PDF/Excel servislerindeki tüm tarih formatlamaları bu yardımcıyı kullanacak şekilde dönüştürüldü. Admin ödeme listesinin tarihleri yerel zamana göre gösteriliyor
- pdf_service.py, excel_service.py: Rapor/fatura dosyaları artık yerel saatle damgalanıyor; relative görseller düzeltilirken sözdizimi hataları giderildi.
- menu.html: Eksik görseller (Bamya Çorbası, Tatlı Esinti) doğru dosya adlarına bağlandı; relative image_url değerleri otomatik /static/images/… yoluna çevriliyor; içecek başlığında icecekler.png kullanılıyor.
- Müşteri ekranında sipariş, sepetim ve sipariş geçmişi hatalı çalışıyordu, hepsi düzeltildi (yönlendirmeler, sipariş faturaları sıralamaları, eski siparişler vb.)
- Admin ekranındaki hızlı işlemler kaldırıldı
- pdf servisi için gerekli olan .env dosyası yeniden eklendi (SAKIN KALDIRMAYIN!!!!)
- Mobil ödeme seçeneği kaldırıldı

****15.10.2025 - 22.10.25 tarihinde yaptığım değişiklikler***
- Sipariş onaylandıktan sonra direkt ödeme ekranına yönlendiriyordu. Artık o ekranda masaya ürün eklemesi yapılabilecek.
Kullanıcı sipariş verir → Sipariş completed durumuna geçer
Kullanıcı "Siparişlerim" sayfasında "Masama Ürün Ekle" butonuna tıklar
Menü sayfasına yönlendirilir ve bilgilendirme mesajı görür
Yeni ürünleri sepete ekler
Sipariş otomatik olarak pending durumuna geçer
Kullanıcı sepete gidip yeni siparişini verebilir
Yeni sipariş mevcut masaya eklenir
- Ablaların yeri yazısına ve logosuna basıldığında ekranlardan çıkış yapıp logine yönlendiriyordu.
Düzeltildi, artık kullanıcının ana sayfasına yönlendiriyor.
- Aktif siparişiniz var pop-up'ındaki iki buton da aynı sayfaya yönlendiriyordu. Artık bu pop-up sadece
sipariş tamamlanmadığında ürünleri görüntülemek için kullanılacak. Tamamlandıktan sonra mevcut siparişiniz
isminde bir pop-up çıkacak. kullanıcı buradan dilerse ürün eklemeye yönlendirilecek, dilerse ödeme adımına
geçebilecek.
- .env dosyası yeniden yazıldı, e-mail gönderim hataları giderildi. (NOLUR SİLME .ENV KRİTİK)
- veritabanındaki değişikliklerden dolayı raporlamada pdf ve excel indir bozulmuştu, düzelttim
- sipariş iptali kısmındaki hataları düzelttim (masalar iptal edilince boş konuma geçiyor)
- müşteri ödeme kısmını kaldırılsın, sadece ödemenn nasıl yapıldğını kasada admin kaydetsin
- rapor kısmını türkçe karakterleri tanımlayacak şekilde yaptım
- arkadaki laciverti kaldırdım

****24.11.2025 tarihinden itibaren yapılan değişiklikler****
- kayıt olmada validate_user_registration metodu silindiği için kayıt olmuyordu, hata giderildi.
- ödemeye yönlendirilen sipariş ödeme yönetimine düşmüyordu düzelttim
- fatura başarıyla gönderildi mesajı çıktığında her seferinde masa detayı ekranına gidiyordu, düzelttim ödeme sayfasındaysa ödeme sayfasında, masa detay sayfasından gönderildiys eo sayfada çıkıyor.
- müşteri isimleri her yerde n/a yazıyordu, düzeldi artık isimler yazıyor.
- admin tarafına şifremi unuttum eklendi.
- iletişim formu eklendi (istek/şikayet)
- yorumlar kısmı ve puanlama özelliği eklendi.
- yazılan kodlar solid prensiplerine göre düzenlendi.