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

---

## Aşama 2 — Alpha-Beta Budaması ve Hamle Sıralaması

### Tasarım Özeti
- **Budama Mantığı (`AlphaBetaSearcher`):** `search.py` içine $\alpha$ (MAX alt sınırı) ve $\beta$ (MIN üst sınırı) takip edilerek `v >= beta` (MAX) ve `v <= alpha` (MIN) durumlarında dalları kesen özyinelemeli arama eklenmiştir.
- **Hamle Sıralama Stratejileri:** Budama verimliliğini ölçmek için üç strateji uygulanmıştır:
  1. `natural`: Sütunları soldan sağa (`0..6`) sırayla dener.
  2. `center`: Merkeze en yakın sütunları önce dener (`3, 2, 4, 1, 5, 0, 6`).
  3. `heuristic`: Bir sonraki durumun terminal/sezgisel değerine göre en umut verici hamleyi önce dener (eşitlikte merkez öncelikli).
- **Doğrulama (`tests/test_search.py`):** 50 rastgele konumda $\alpha$-$\beta$'nın Minimax ile birebir aynı değeri ürettiği ve üç sıralama stratejisinin de doğru budama yaptığı birim testleriyle doğrulanmıştır (toplam 11/11 test `OK`).

### Minimax vs. Alpha-Beta Düğüm Karşılaştırması (Derinlik 4 ve 6)

| Konum | Derinlik ($d$) | Minimax (`MM`) | AB (`natural`) | AB (`center`) | AB (`heuristic`) | En İyi Azalma (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | 6 | 137.249 | 1.247 | 1.247 | 1.247 | %99.09 |
| **P2** | 4 | 2.798 | 172 | 171 | 171 | %93.89 |
| **P2** | 6 | 130.993 | 2.473 | 2.636 | 1.930 | %98.53 |
| **P3** | 4 | 2.041 | 85 | 449 | 91 | %95.84 |
| **P3** | 6 | 78.677 | 495 | 9.521 | 557 | %99.37 |
| **P4** | 4 | 2.217 | 212 | 422 | 125 | %94.36 |
| **P4** | 6 | 84.785 | 1.595 | 4.943 | 759 | %99.10 |
| **P5** | 4 | 2.125 | 328 | 178 | 89 | %95.81 |
| **P5** | 6 | 88.904 | 4.568 | 864 | 199 | %99.78 |

### Kısa Değerlendirme
- **Budama kazanımı:** Derinlik 6'da $\alpha$-$\beta$ budaması, Minimax'e kıyasla ziyaret edilen düğüm sayısını tüm konumlarda **%98,5 ile %99,78** arasında azaltmıştır.
- **Hamle sıralamasının etkisi:** `P3` konumunda kazan

---

## Aşama 3 — Sezgisel Değerlendirme Fonksiyonu (`evaluate.py`)

### Tasarım Özeti
- **Pencere Tabanlı Puanlama (`_iter_windows`, `score_window`):** Tahtadaki tüm $K=5$ uzunluğundaki dikey, yatay ve çapraz pencereler ($V=1$ silindir kenar sarma dahil) taranır. Hem MAX hem MIN taşı içeren kilitli pencereler `0` puan alır; tek oyuncuya ait pencereler taş sayısına göre artan ağırlıklarla (`1: 1.0`, `2: 5.0`, `3: 25.0`, `4: 150.0`) puanlanır.
- **Merkez Kontrolü (`center_control_score`):** Merkez sütuna yakın taşlara küçük pozisyonel bonus eklenir.
- **Normalizasyon ve Sınır Garantisi (`evaluate`):** Terminal durumlarda kesin fayda (`-1.0`, `0.0`, `+1.0`) döndürülür. Terminal olmayan durumlarda toplam ham skor `0.95 * tanh(raw_score / 250.0)` ile `(-0.95, +0.95)` aralığına sıkıştırılarak terminal değerlerin asla aşılmaması garanti edilir.
- **Birim Testleri (`tests/test_evaluate.py`):** Boş tahta sıfır kontrolü, sınır garantisi, MAX/MIN simetrisi, silindir sarma tehdidi ve terminal doğrulama dahil **5 birim testi** başarıyla (`OK`) geçmiştir.

### `zero_eval` vs. `evaluate` Konum Karşılaştırması ($d=4$, `heuristic` sıralama)

| Konum | `zero_eval` Hamle / Skor / Düğüm | `evaluate` Hamle / Skor / Düğüm |
| :--- | :---: | :---: |
| **P1** | `3` / `+0.000` / `172` | `2` / `-0.004` / `293` |
| **P2** | `3` / `+0.000` / `171` | `2` / `+0.000` / `192` |
| **P3** | `0` / `+1.000` / `91` | `0` / `+1.000` / `85` |
| **P4** | `1` / `+0.000` / `125` | `1` / `-0.068` / `142` |
| **P5** | `4` / `+1.000` / `89` | `4` / `+1.000` / `97` |

### Karşılıklı Maç Testi ($d=4$, `AlphaBetaSearcher`)

| Eşleşme | Sonuç (MAX Açısından) | Toplam Hamle |
| :--- | :---: | :---: |
| **Eval (MAX) vs. Zero (MIN)** | `+1` (Eval Kazandı) | 35 |
| **Zero (MAX) vs. Eval (MIN)** | `0` (Beraberlik) | 35 |

### Kısa Değerlendirme
- **Oyun gücü:** Sezgisel değerlendirme kullanan ajan, `zero_eval` karşısında ilk oyuncu olarak kazanmış, ikinci oyuncu olarak ise yenilmeden berabere kalmıştır (toplam 1.5 / 2 puan).
- **Düğüm sayısı farkı:** `zero_eval` tüm terminal olmayan yapraklarda aynı değeri (`0.0`) döndürdüğü için eşitlikten dolayı agresif budama yapmaktadır. `evaluate` ise farklı pozisyonel değerler ürettiğinden `P1` ve `P2`'de bir miktar daha fazla düğüm gezmekte (`172 → 293`), ancak buna karşılık taktik olmayan konumlarda çok daha anlamlı hamleler seçmektedir.

---

## Aşama 4 — İteratif Derinleştirme, Zaman Sınırı ve Geçiş Tablosu (TT)

### Tasarım Özeti
- **İteratif Derinleştirme (`IterativeDeepeningSearcher`):** Derinlik $d = 1, 2, 3, \dots$ şeklinde kademeli artırılarak arama yapılır. Belirlenen zaman sınırı dolduğunda (`SearchTimeout`), yarıda kalan derinlik atılır ve en son **tamamlanan** derinliğin en iyi hamlesi güvenli şekilde döndürülür.
- **PV ve TT Hamle Önceliği:** Önceki derinlikte veya Geçiş Tablosunda (*Transposition Table*) en iyi seçilen hamle bir sonraki derinlikte ilk sırada denenerek budama verimliliği artırılır.
- **Erken Sonlanma:** Kök düğümde kesin kazanma (`+1.0` veya `-1.0`) bulunduğu anda daha derine inmeden arama sonlandırılır.
- **Birim Testleri (`tests/test_search.py`):** Zaman sınırı uyumu, sabit derinlikte TT–Alpha-Beta değer eşitliği, TT isabet (*hit*) kontrolü ve tek hamlede kazanmada erken durma testleri başarıyla (`OK`) geçmiştir.

### Geçiş Tablosu (TT) Karşılaştırması (`max_depth=5`, `heuristic` sıralama)

| Konum | TT Kapalı (`d` / Düğüm / Süre) | TT Açık (`d` / Düğüm / TT Hit / Süre) | Düğüm Azalması |
| :--- | :---: | :---: | :---: |
| **P1** | `5` / `1.612` / `0.679s` | `5` / `1.453` / `62` / `0.239s` | %9.86 |
| **P2** | `5` / `1.375` / `0.208s` | `5` / `936` / `26` / `0.141s` | %31.93 |
| **P3** | `1` / `7` / `0.001s` | `1` / `7` / `0` / `0.001s` | Erken sonlanma |
| **P4** | `5` / `411` / `0.064s` | `5` / `375` / `5` / `0.083s` | %8.76 |
| **P5** | `1` / `7` / `0.001s` | `1` / `7` / `0` / `0.005s` | Erken sonlanma |

### Zaman Sınırı Ölçümleri (`P2` Konumu, `TT=True`)

| Zaman Sınırı | Tamamlanan Derinlik ($d$) | Seçilen Hamle | Skor | Düğüm | TT Hit | Gerçekleşen Süre |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `0.1s` | 4 | 2 | `+0.000` | 384 | 9 | `0.127s` |
| `0.5s` | 5 | 2 | `+0.110` | 1.920 | 104 | `0.510s` |
| `1.0s` | 6 | 3 | `-0.068` | 5.248 | 304 | `1.003s` |

### Kısa Değerlendirme
- **TT verimliliği:** Aynı tahta durumlarına farklı hamle sıralarıyla ulaşıldığında TT yeniden aramayı engellemiş; `P2`'de düğüm sayısını **%31,93** azaltmış, `P1`'de ise çalışma süresini `0.679s`'den `0.239s`'ye indirmiştir.
- **Zaman yönetimi ve derinlik artışı:** Süre bütçesi arttıkça ajan düzenli olarak daha derine inmiştir (`0.1s → d=4`, `0.5s → d=5`, `1.0s → d=6`). Derinlik 6'da artan TT isabet sayısı (`304`) derinleştikçe tablonun katkısının büyüdüğünü göstermektedir.
- **Erken kazanma tespiti:** `P3` ve `P5` konumlarında tek hamlede kazanma bulunduğu için arama $d=1$'de sadece 7 düğüm gezerek anında tamamlanmıştır.
