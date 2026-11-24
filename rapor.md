# Connect-K Yapay Zekâ Ajanı — Proje Raporu

**Varyant Parametreleri:** $R = 5$, $C = 7$, $K = 5$, $V = 1$ (Silindir Modu), $d = 30$

---

## Aşama 0 — Oyun Modeli ve Doğrulama

### Tasarım Özeti
- **Durum Temsili (`State`):** Değişmez (*immutable*) `dataclass` yapısı ile 2 boyutlu tahta, sıradaki oyuncu ve son hamle bilgisi tutulmuştur. Her `result(state, action)` çağrısı orijinal durumu bozmadan yeni bir durum döndürür.
- **Oyun Kuralları (`Game`):** Yerçekimi kuralı, dolu sütunların yasal hamlelerden çıkarılması, $K=5$ kazanma kontrolü ve $V=1$ (Silindir) varyantı için yatay/çapraz kenar sarma (*wrap-around*) mantığı uygulanmıştır.
- **Birim Testleri (`tests/test_game.py`):** Boş tahta `perft`, dolu sütun kontrolü, dikey kazanma, yatay/çapraz silindir kazanma ve Misère ($V=2$) senaryolarını kapsayan **6 birim testi** `0.014s` içinde başarıyla (`OK`) geçmiştir.

### Boş Tahta `perft` Ölçüm Tablosu

| Derinlik ($n$) | Yaprak Düğüm Sayısı ($7^n$) | Süre (sn) |
| :---: | :---: | :---: |
| 1 | 7 | 0.0000 |
| 2 | 49 | 0.0006 |
| 3 | 343 | 0.0018 |
| 4 | 2.401 | 0.0121 |
| 5 | 16.807 | 0.1088 |

---

## Aşama 1 — Derinlik Sınırlı Minimax

### Tasarım Özeti
- **Arama Yapısı (`search.py`):** Terminal durum kontrolü derinlik kontrolünden önce yapılacak şekilde `max_value` ve `min_value` özyinelemeleri yazılmıştır.
- **Geçici Değerlendirme:** Derinlik 0'da tüm yaprak düğümler için `0.0` döndüren `zero_eval` fonksiyonu kullanılmıştır.
- **Deterministik Seçim ve Sayaçlar:** Eşit değerli hamlelerde merkeze en yakın sütun (`C=7` için sütun `3`) seçilir. Her düğüm ziyaretinde `nodes` sayacı artırılır ve etkin dallanma çarpanı $b_{\text{etkin}} = \text{nodes}^{1/d}$ hesaplanır.
- **Birim Testleri (`tests/test_search.py`):** Tek hamlede kazanma, tek hamlede rakip tehdidini engelleme ve deterministik düğüm sayısı kontrollerini içeren **3 birim testi** `0.002s` içinde başarıyla (`OK`) geçmiştir.

### Test Konumları (Tekrarlanabilirlik İçin Hamle Dizileri)
- **P1:** `[]` (Boş tahta)
- **P2:** `[3, 3, 4, 4]` (Merkez açılış)
- **P3:** `[0, 1, 0, 1, 0, 1, 0, 2]` (MAX için sütun 0'da tek hamlede dikey kazanma)
- **P4:** `[0, 1, 2, 1, 3, 1, 4, 1]` (MIN tehdidini sütun 1'de tek hamlede engelleme)
- **P5:** `[5, 3, 6, 3, 0, 3, 1, 2]` (MAX için sütun 4'te silindir sarma ile yatay kazanma)

### Ölçüm Tablosu (Derinlik 2, 4, 6)

| Konum | Derinlik ($d$) | Seçilen Hamle | Ziyaret Edilen Düğüm | Etkin Dallanma Çarpanı ($b_{\text{etkin}}$) |
| :--- | :---: | :---: | :---: | :---: |
| **P1** | 2 | 3 | 56 | 7.48 |
| **P1** | 4 | 3 | 2.800 | 7.27 |
| **P1** | 6 | 3 | 137.249 | 7.18 |
| **P2** | 2 | 3 | 56 | 7.48 |
| **P2** | 4 | 3 | 2.798 | 7.27 |
| **P2** | 6 | 3 | 130.993 | 7.13 |
| **P3** | 2 | 0 | 49 | 7.00 |
| **P3** | 4 | 0 | 2.041 | 6.72 |
| **P3** | 6 | 0 | 78.677 | 6.55 |
| **P4** | 2 | 1 | 55 | 7.42 |
| **P4** | 4 | 1 | 2.217 | 6.86 |
| **P4** | 6 | 1 | 84.785 | 6.63 |
| **P5** | 2 | 4 | 49 | 7.00 |
| **P5** | 4 | 4 | 2.125 | 6.79 |
| **P5** | 6 | 4 | 88.904 | 6.68 |

### Kısa Değerlendirme
- **Taktik doğruluk:** Minimax, `P3`'te dikey kazanmayı (`0`), `P4`'te rakibin kazanmasını engellemeyi (`1`) ve `P5`'te silindir kenar sarma kazanmasını (`4`) tüm derinliklerde doğru seçmiştir.
- **Düğüm büyümesi:** Budama olmadığı için boş tahtada (`P1`) düğüm sayısı her derinlikte yaklaşık $C = 7$ kat büyümekte, $d=6$'da 137 bin düğüme ulaşmaktadır.
- **Erken sonlanma etkisi:** `P3`, `P4` ve `P5` konumlarında kazanma durumlarına erken ulaşıldığı için terminal düğümler alt ağaçları kesmekte ve $b_{\text{etkin}}$ değeri `6.55–6.68` bandına düşmektedir.