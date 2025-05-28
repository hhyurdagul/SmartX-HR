-- ============================================================================
-- BİRLEŞTİRİLMİŞ ÖRNEK VERİ GİRİŞİ BETİĞİ
-- ============================================================================
-- Not: Tarihler YYYY-AA-GG formatındadır.
-- ÖNEMLİ GÜVENLİK UYARISI: 'users' tablosundaki 'password' alanı düz metin
-- olarak saklanmaktadır. Bu, GERÇEK UYGULAMALAR İÇİN KESİNLİKLE GÜVENSİZDİR.
-- Parolalar her zaman güvenli bir şekilde hash'lenerek saklanmalıdır.
-- ============================================================================

-- # Users Tablosu için Genişletilmiş Örnek Veriler (@smartiks.com.tr domaini ile)
-- (ID: 1-30)
INSERT INTO users (user_id, username, email, role, start_date, password) VALUES
(0, 'admin', 'admin@smartiks.com.tr', 'admin', '2000-01-01', 'admin123'),
(1, 'emre.aksoy', 'emre.aksoy@smartiks.com.tr', 'Yazılım Mühendisi', '2023-02-10', 'passEmre1'),
(2, 'elif.bulut', 'elif.bulut@smartiks.com.tr', 'Arka Uç Geliştirici', '2022-08-15', 'passElif2'),
(3, 'burak.deniz', 'burak.deniz@smartiks.com.tr', 'Ön Uç Geliştirici', '2023-05-20', 'passBurak3'),
(4, 'deniz.arslan', 'deniz.arslan@smartiks.com.tr', 'Veri Bilimci', '2021-11-01', 'passDeniz4'),
(5, 'gamze.yildiz', 'gamze.yildiz@smartiks.com.tr', 'Proje Yöneticisi', '2020-06-01', 'passGamze5'),
(6, 'serkan.ozkan', 'serkan.ozkan@smartiks.com.tr', 'DevOps Mühendisi', '2022-01-15', 'passSerkan6'),
(7, 'pinar.sahin', 'pinar.sahin@smartiks.com.tr', 'Test Mühendisi', '2023-09-01', 'passPinar7'),
(8, 'murat.aydin', 'murat.aydin@smartiks.com.tr', 'UI/UX Tasarımcısı', '2022-12-05', 'passMurat8'),
(9, 'esra.koc', 'esra.koc@smartiks.com.tr', 'Sistem Yöneticisi', '2021-04-10', 'passEsra9'),
(10, 'volkan.gunes', 'volkan.gunes@smartiks.com.tr', 'Teknik Lider', '2019-10-01', 'passVolkan10'),
(11, 'irem.tekin', 'irem.tekin@smartiks.com.tr', 'Çözüm Mimarı', '2020-03-15', 'passIrem11'),
(12, 'baris.cetin', 'baris.cetin@smartiks.com.tr', 'İş Analisti', '2023-07-01', 'passBaris12'),
(13, 'asli.korkmaz', 'asli.korkmaz@smartiks.com.tr', 'Güvenlik Uzmanı', '2022-10-20', 'passAsli13'),
(14, 'kaan.dogan', 'kaan.dogan@smartiks.com.tr', 'Yazılım Mühendisi', '2024-01-05', 'passKaan14'),
(15, 'zeynep.avci', 'zeynep.avci@smartiks.com.tr', 'Arka Uç Geliştirici', '2023-11-10', 'passZeynep15'),
(16, 'mustafa.sari', 'mustafa.sari@smartiks.com.tr', 'Ön Uç Geliştirici', '2024-03-01', 'passMustafa16'),
(17, 'selin.efe', 'selin.efe@smartiks.com.tr', 'Veri Analisti', '2022-09-12', 'passSelin17'),
(18, 'onur.bas', 'onur.bas@smartiks.com.tr', 'DevOps Mühendisi', '2023-04-18', 'passOnur18'),
(19, 'ece.kurt', 'ece.kurt@smartiks.com.tr', 'Test Mühendisi', '2024-02-15', 'passEce19'),
(20, 'cem.ozturk', 'cem.ozturk@smartiks.com.tr', 'Yazılım Mühendisi', '2022-07-25', 'passCem20'),
(21, 'ayla.can', 'ayla.can@smartiks.com.tr', 'Proje Yöneticisi', '2021-09-05', 'passAyla21'),
(22, 'gokhan.tas', 'gokhan.tas@smartiks.com.tr', 'Teknik Lider', '2020-11-30', 'passGokhan22'),
(23, 'seda.toprak', 'seda.toprak@smartiks.com.tr', 'UI/UX Tasarımcısı', '2023-06-22', 'passSeda23'),
(24, 'ugur.vural', 'ugur.vural@smartiks.com.tr', 'Sistem Yöneticisi', '2022-03-14', 'passUgur24'),
(25, 'derya.kaplan', 'derya.kaplan@smartiks.com.tr', 'İş Analisti', '2024-04-01', 'passDerya25'),
(26, 'levent.yilmaz', 'levent.yilmaz@smartiks.com.tr', 'Yazılım Mühendisi', '2023-08-20', 'passLevent26'),
(27, 'merve.kaya', 'merve.kaya@smartiks.com.tr', 'Arka Uç Geliştirici', '2024-05-10', 'passMerve27'),
(28, 'orhan.demir', 'orhan.demir@smartiks.com.tr', 'Veri Bilimci', '2022-06-01', 'passOrhan28'),
(29, 'pelin.ates', 'pelin.ates@smartiks.com.tr', 'Test Mühendisi', '2023-10-05', 'passPelin29'),
(30, 'tarkan.sevinc', 'tarkan.sevinc@smartiks.com.tr', 'DevOps Mühendisi', '2021-12-20', 'passTarkan30');

-- # KPI Category Tablosu Örnek Verileri
-- (ID: 1-4)
INSERT INTO kpi_categories (category_id, category_name) VALUES
(1, 'Teknik Performans'),
(2, 'Proje Yönetimi'),
(3, 'Takım Çalışması ve İletişim'),
(4, 'Kişisel Gelişim');

-- # Training Courses Tablosu Örnek Verileri
-- (ID: 1-6)
INSERT INTO training_courses (training_course_id, course_name, description, duration_hours) VALUES
(1, 'İleri Python Programlama', 'Nesne yönelimli programlama, dekoratörler ve gelişmiş kütüphaneler.', 40),
(2, 'React ile Modern Web Geliştirme', 'Component yapısı, state yönetimi ve React hookları.', 30),
(3, 'AWS Bulut Bilişim Temelleri', 'EC2, S3, RDS ve temel AWS servisleri hakkında giriş eğitimi.', 20),
(4, 'Agile ve Scrum Metodolojileri', 'Çevik yazılım geliştirme prensipleri ve Scrum uygulama esasları.', 16),
(5, 'Kubernetes Yönetimi', 'Konteyner orkestrasyonu ve Kubernetes cluster yönetimi.', 35),
(6, 'Veritabanı Optimizasyonu', 'SQL sorgu optimizasyonu ve indeksleme teknikleri.', 24);

-- # KPIs Tablosu Örnek Verileri (kpi_categories'e bağlı)
-- (ID: 1-7)
INSERT INTO kpis (kpi_id, category_id, kpi_name, unit, description) VALUES
(1, 1, 'Kod Kalitesi Puanı', 'puan (1-10)', 'Yazılan kodun belirlenen standartlara uygunluk ve temizlik puanı.'),
(2, 1, 'Hata Düzeltme Hızı', 'saat', 'Bir hatanın raporlanmasından çözülmesine kadar geçen ortalama süre.'),
(3, 2, 'Proje Zamanında Tamamlama Oranı', '%', 'Atanan görevlerin/projelerin belirlenen süre içinde bitirilme yüzdesi.'),
(4, 2, 'Bütçe Yönetimi', '%', 'Proje bütçesinin aşılma veya altında kalma oranı.'),
(5, 4, 'Tamamlanan Eğitim Sayısı', 'adet', 'Belirli bir dönemde tamamlanan şirket içi veya dışı eğitim sayısı.'),
(6, 1, 'Birim Test Kapsamı', '%', 'Yazılan kodun birim testler ile kapsanma oranı.'),
(7, 3, 'Mentorluk Aktivitesi', 'adet', 'Yeni ekip üyelerine yapılan mentorluk/destek sayısı.');

-- # Teams Tablosu Örnek Verileri (users'a bağlı - team_lead_user_id)
-- (ID: 1-4)
INSERT INTO teams (team_id, team_name, description, team_lead_user_id) VALUES
(1, 'Alfa Geliştirme Takımı', 'Çekirdek ürün geliştirme ve ana iş mantığı.', 10), -- Lider: Volkan Güneş (user_id=10)
(2, 'Platform ve Altyapı Takımı', 'DevOps, CI/CD, bulut altyapı ve sistem yönetimi.', 6), -- Lider: Serkan Özkan (user_id=6)
(3, 'Mobil Uygulama Takımı', 'iOS ve Android uygulamaları geliştirme ve bakım.', 22), -- Lider: Gökhan Taş (user_id=22)
(4, 'Veri Ekibi', 'Veri analizi, mühendisliği ve makine öğrenmesi modelleri.', 4);  -- Lider: Deniz Arslan (user_id=4)

-- # Leave Balances Tablosu Örnek Verileri (users'a bağlı)
-- (ID: 1-30)
INSERT INTO leave_balances (leave_balance_id, user_id, total_days, used_days, remaining_days) VALUES
(1, 1, 20, 5, 15),   -- Emre Aksoy
(2, 2, 22, 2, 20),   -- Elif Bulut
(3, 3, 20, 0, 20),   -- Burak Deniz
(4, 4, 25, 0, 25),   -- Deniz Arslan
(5, 5, 25, 1, 24),   -- Gamze Yıldız
(6, 6, 22, 0, 22),   -- Serkan Özkan
(7, 7, 20, 0, 20),   -- Pınar Şahin
(8, 8, 22, 0, 22),   -- Murat Aydın
(9, 9, 25, 5, 20),   -- Esra Koç
(10, 10, 30, 10, 20), -- Volkan Güneş
(11, 11, 25, 3, 22),  -- İrem Tekin
(12, 12, 20, 0, 20),  -- Barış Çetin
(13, 13, 22, 2, 20),  -- Aslı Korkmaz
(14, 14, 15, 0, 15),  -- Kaan Doğan
(15, 15, 18, 0, 18),  -- Zeynep Avcı
(16, 16, 15, 0, 15),  -- Mustafa Sarı
(17, 17, 22, 0, 22),  -- Selin Efe
(18, 18, 20, 4, 16),  -- Onur Baş
(19, 19, 15, 0, 15),  -- Ece Kurt
(20, 20, 22, 0, 22),  -- Cem Öztürk
(21, 21, 25, 8, 17),  -- Ayla Can
(22, 22, 30, 5, 25),  -- Gökhan Taş
(23, 23, 20, 1, 19),  -- Seda Toprak
(24, 24, 22, 6, 16),  -- Uğur Vural
(25, 25, 15, 0, 15),  -- Derya Kaplan
(26, 26, 20, 0, 20),  -- Levent Yılmaz
(27, 27, 15, 0, 15),  -- Merve Kaya
(28, 28, 22, 3, 19),  -- Orhan Demir
(29, 29, 18, 0, 18),  -- Pelin Ateş
(30, 30, 25, 0, 25);   -- Tarkan Sevinç

-- # Leave Requests Tablosu Örnek Verileri (users'a bağlı)
-- (ID: 1-8)
INSERT INTO leave_requests (leave_request_id, user_id, leave_type, start_date, end_date, reason, status) VALUES
(1, 1, 'Yıllık İzin', '2025-05-10', '2025-05-14', 'Bahar tatili.', 'onaylandı'), -- Emre Aksoy
(2, 2, 'Hastalık İzni', '2025-04-01', '2025-04-02', 'Soğuk algınlığı.', 'onaylandı'), -- Elif Bulut
(3, 14, 'Yıllık İzin', '2025-07-20', '2025-07-30', 'Yaz tatili.', 'beklemede'), -- Kaan Doğan
(4, 5, 'Mazeret İzni', '2025-04-15', '2025-04-15', 'Resmi işlem.', 'onaylandı'), -- Gamze Yıldız
(5, 20, 'Yıllık İzin', '2025-06-01', '2025-06-10', 'Dinlenme.', 'beklemede'), -- Cem Öztürk
(6, 7, 'Doğum İzni', '2025-08-01', '2025-11-30', 'Doğum izni başlangıcı.', 'onaylandı'), -- Pınar Şahin
(7, 17, 'Hastalık İzni', '2025-03-10', '2025-03-11', 'Migren atağı.', 'reddedildi'), -- Selin Efe
(8, 30, 'Yıllık İzin', '2025-09-01', '2025-09-05', 'Kısa mola.', 'beklemede'); -- Tarkan Sevinç

-- # KPI Results Tablosu Örnek Verileri (kpis ve users'a bağlı)
-- (ID: 1-10)
INSERT INTO kpi_results (result_id, kpi_id, user_id, period, target, actual_value) VALUES
(1, 1, 1, '2025-Q1', 8, 9),     -- Emre Aksoy, Kod Kalitesi
(2, 6, 1, '2025-Q1', 75, 80),   -- Emre Aksoy, Test Kapsamı
(3, 2, 2, '2025-Q1', 8, 6),     -- Elif Bulut, Hata Düzeltme
(4, 3, 5, '2024-Yıl', 90, 92),   -- Gamze Yıldız, Proje Tamamlama
(5, 7, 10, '2024-Yıl', 3, 5),   -- Volkan Güneş, Mentorluk
(6, 5, 14, '2024-Yıl', 1, 2),   -- Kaan Doğan, Eğitim Sayısı
(7, 1, 15, '2025-Q1', 8, 8),   -- Zeynep Avcı, Kod Kalitesi
(8, 6, 16, '2025-Q1', 80, 70),   -- Mustafa Sarı, Test Kapsamı
(9, 3, 21, '2025-Q1', 95, 98),   -- Ayla Can, Proje Tamamlama
(10, 5, 30, '2024-Yıl', 2, 1);   -- Tarkan Sevinç, Eğitim Sayısı

-- # User Training Progress Tablosu Örnek Verileri (users ve training_courses'a bağlı)
-- (ID: 1-10)
INSERT INTO user_training_progress (progress_id, user_id, training_course_id, enrollment_date, completion_percentage, is_completed) VALUES
(1, 1, 1, '2024-10-01', 100.0, TRUE),  -- Emre Aksoy, Python (Kurs ID: 1)
(2, 2, 2, '2025-01-15', 80.0, FALSE), -- Elif Bulut, React (Kurs ID: 2)
(3, 3, 2, '2025-02-01', 100.0, TRUE), -- Burak Deniz, React (Kurs ID: 2)
(4, 6, 3, '2024-11-20', 100.0, TRUE), -- Serkan Özkan, AWS (Kurs ID: 3)
(5, 6, 5, '2025-03-01', 40.0, FALSE), -- Serkan Özkan, Kubernetes (Kurs ID: 5)
(6, 9, 6, '2025-01-10', 100.0, TRUE), -- Esra Koç, Veritabanı (Kurs ID: 6)
(7, 14, 1, '2024-11-01', 60.0, FALSE), -- Kaan Doğan, Python (Kurs ID: 1)
(8, 18, 5, '2025-03-15', 10.0, FALSE), -- Onur Baş, Kubernetes (Kurs ID: 5)
(9, 25, 4, '2024-12-01', 100.0, TRUE), -- Derya Kaplan, Agile (Kurs ID: 4)
(10, 28, 6, '2025-02-20', 90.0, FALSE); -- Orhan Demir, Veritabanı (Kurs ID: 6)

-- # Projects Tablosu Örnek Verileri (teams'e bağlı)
-- (ID: 1-6)
INSERT INTO projects (project_id, project_name, description, start_date, end_date, team_id, status) VALUES
(1, 'Müşteri Yönetim Sistemi V3', 'Mevcut CRM sisteminin microservis mimarisine taşınması.', '2025-01-15', '2026-01-14', 1, 'geliştirme'), -- Alfa Takımı (Team ID: 1)
(2, 'Veri Ambarı ETL Süreçleri', 'Yeni ETL süreçlerinin tasarımı ve uygulanması.', '2025-02-01', '2025-10-31', 4, 'geliştirme'), -- Veri Ekibi (Team ID: 4)
(3, 'CI/CD Güvenlik Taramaları', 'CI/CD pipelinelarına otomatik güvenlik tarama adımları eklenmesi.', '2025-04-01', '2025-07-31', 2, 'planlama'), -- Platform Takımı (Team ID: 2)
(4, 'Mobil Ödeme Entegrasyonu', 'Mobil uygulamaya yeni ödeme sistemi entegrasyonu.', '2024-11-01', '2025-05-30', 3, 'test'), -- Mobil Takımı (Team ID: 3)
(5, 'Eski Raporlama Servisi Kapatma', 'Kullanımdan kalkan eski raporlama servisinin devreden çıkarılması.', '2024-09-01', '2025-03-31', 4, 'tamamlandı'), -- Veri Ekibi (Team ID: 4)
(6, 'AI Destekli Öneri Motoru', 'Kullanıcı davranışlarına göre ürün öneri motoru geliştirme.', '2025-06-01', '2026-03-31', 1, 'planlama'); -- Alfa Takımı (Team ID: 1)

-- # Team Members Tablosu Örnek Verileri (teams ve users'a bağlı)
-- (ID: 1-29)
INSERT INTO team_members (team_member_id, team_id, user_id, role_in_team) VALUES
-- Alfa Takımı (Team ID: 1)
(1, 1, 10, 'Takım Lideri'),     -- Volkan Güneş
(2, 1, 1, 'Yazılım Geliştirici'), -- Emre Aksoy
(3, 1, 2, 'Arka Uç Geliştirici'), -- Elif Bulut
(4, 1, 14, 'Yazılım Geliştirici'), -- Kaan Doğan
(5, 1, 15, 'Arka Uç Geliştirici'), -- Zeynep Avcı
(6, 1, 20, 'Yazılım Geliştirici'), -- Cem Öztürk
(7, 1, 26, 'Yazılım Geliştirici'), -- Levent Yılmaz
(8, 1, 5, 'Proje Koordinatörü'), -- Gamze Yıldız
(9, 1, 12, 'İş Analisti'),       -- Barış Çetin
-- Platform Takımı (Team ID: 2)
(10, 2, 6, 'Takım Lideri / DevOps'), -- Serkan Özkan
(11, 2, 9, 'Sistem Yöneticisi'),    -- Esra Koç
(12, 2, 13, 'Güvenlik Uzmanı'),      -- Aslı Korkmaz
(13, 2, 18, 'DevOps Mühendisi'),     -- Onur Baş
(14, 2, 24, 'Sistem Yöneticisi'),    -- Uğur Vural
(15, 2, 30, 'DevOps Mühendisi'),     -- Tarkan Sevinç
-- Mobil Takımı (Team ID: 3)
(16, 3, 22, 'Takım Lideri'),         -- Gökhan Taş
(17, 3, 3, 'Ön Uç Geliştirici (React Native)'), -- Burak Deniz
(18, 3, 8, 'UI/UX Tasarımcısı'),      -- Murat Aydın
(19, 3, 16, 'Ön Uç Geliştirici (Swift/Kotlin)'), -- Mustafa Sarı
(20, 3, 23, 'UI/UX Tasarımcısı'),      -- Seda Toprak
(21, 3, 27, 'Arka Uç Geliştirici (Mobil API)'), -- Merve Kaya
(22, 3, 7, 'Test Mühendisi'),         -- Pınar Şahin
(23, 3, 19, 'Test Mühendisi'),         -- Ece Kurt
-- Veri Ekibi (Team ID: 4)
(24, 4, 4, 'Takım Lideri / Veri Bilimci'), -- Deniz Arslan
(25, 4, 11, 'Çözüm Mimarı (Veri)'),      -- İrem Tekin
(26, 4, 17, 'Veri Analisti'),           -- Selin Efe
(27, 4, 21, 'Proje Yöneticisi (Veri Projeleri)'), -- Ayla Can
(28, 4, 28, 'Veri Mühendisi'),          -- Orhan Demir
(29, 4, 25, 'İş Analisti (Raporlama)'),   -- Derya Kaplan
(30, 4, 29, 'Kalite Güvence (Veri)');   -- Pelin Ateş

-- ============================================================================
-- BİTİŞ: BİRLEŞTİRİLMİŞ ÖRNEK VERİ GİRİŞİ BETİĞİ
-- ============================================================================