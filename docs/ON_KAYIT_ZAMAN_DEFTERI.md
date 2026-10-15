# Ön kayıt zaman defteri (2026-10-09)

**Kaynak:** Ana oturum dökümündeki araç çağrısı kayıtları. Bu kayıtları uygulama tuttu; zamanlar UTC. Defterde yalnızca dosya adları, araç adları ve zamanlar var. Sohbet içeriği yok.

**Neden gerekti:** Denetim raporunun B1 bulgusu, ön kayıt dosyalarının Windows "oluşturma zamanına" bakarak dosyaların koşulardan sonra yazıldığı sonucuna vardı. Ama Claude Code'un Write ve Edit araçları dosyayı yerinde düzenlemiyor, yenisiyle değiştiriyor. Bu yüzden oluşturma zamanı, dosyanın en son düzenlendiği ana kayıyor. Yerinde ekleme yapan araçlar (PowerShell `Add-Content`, Python `write_text`) ise oluşturma zamanını koruyor.

**Kanıtlar:**
- `DENETIM_ISTEMI.md` ilk kez 2026-10-08T23:54:34Z'de yazıldı. Dosya sistemi ise oluşturma zamanı olarak 2026-10-09 16:06:42'yi (UTC+3), yani son Edit'in zamanını (13:06:41Z) gösteriyor.
- `DURUM.md` 7–8 Ekim'den beri var. Oluşturma zamanı ise bugünkü son Edit'in zamanı.
- Denetçinin tablosundaki her "oluşturma" zamanı, o dosyaya sonuçları ekleyen son Edit'in zamanıyla saniyesine kadar aynı. Örnek: FAZ4C'de 02:52:11 (+03), yani 23:52:11Z.

| Faz | Ön kaydın ilk yazımı (Write) | İlk hakem çağrısı | Fark | Sonuçların eklenmesi (Edit) |
|---|---|---|---|---|
| 4c | 2026-10-07 23:45:25 | 23:45:36 | 11 sn önce | 23:52:11 |
| 4d | 23:58:39 | 23:58:46 | 7 sn önce | 23:59:47 |
| 4e | 2026-10-08 02:57:49 | 02:57:59 | 10 sn önce | 02:59:32, 03:04:25 |
| 5 | 03:18:30 | 03:18:50 | 20 sn önce | Ek ön kayıt 03:21:41 (C turundan sonra; S, K ve takip mesajlarından önce). Sonuçlar 03:28:29 |
| 6a | 04:00:43 | 04:00:58 | 14 sn önce | 04:03:29 |
| 6b | 12:24:49 (Edit ile ek ön kayıt) | 12:24:56 | 7 sn önce | 12:27:12 |
| 7 | 12:38:10 | 12:38:23 | 13 sn önce | 12:41:50 |
| 8 | 14:08:00 | 14:09:11 | 72 sn önce | 14:16:02 |
| 9 | 14:23:19 | 14:23:28 | 10 sn önce | 14:26:05 |
| 10 | 14:30:24 | 14:30:39 | 15 sn önce | 14:35:23, 14:37:57, 14:38:39 |
| 11 | 2026-10-09 00:30:34 | 00:31:22 | 48 sn önce | 00:37:43, 00:40:28, 00:52:33 (`Add-Content`) |

**İçerik kontrolü:** Her dosyanın ilk yazılan halindeki satırların hepsi (FAZ4C–FAZ11) bugünkü dosyada da kelimesi kelimesine duruyor; eksik satır 0. Sonraki her Edit yalnızca ekleme yapmış: var olan bir satırın ardına yeni bölüm koymuş. Önceden yazılmış tahminlerin hiçbiri değiştirilmemiş.

Faz 1–3 denetimin kapsamında değildi:
- FAZ1 ve FAZ3a'da değişen tek satır "Durum: Kullanıcı onayı bekliyor". O da koşudan önce "onaylandı" olarak güncellenmiş.
- FAZ3b'de bundan başka bir kural satırı da değişmiş. Bu değişiklik, kural dondurulmadan önce geliştirme setinde yapılmış ve dosyada "Geliştirme seti sonucu (dondurmadan önce)" diye yazılı. Betikler `scratchpad/onkayit_zaman.py` ve `onkayit_degisim.py`.

**Sınır:** Bu kanıt özel ana sohbet dökümüne dayanıyor ve dışarıdan doğrulanamıyor. Denetçinin önerisi kabul edildi: Bundan sonra her ön kayıt, koşudan önce dışarıda zaman damgası alan bir yere de konacak (ör. herkese açık bir git deposuna gönderim ya da kendine e-posta).

## Faz 14 parmak izleri (koşudan önce, 2026-10-11)
Kullanıcı bu üç satırı kendine e-postayla gönderecek. E-postanın zamanı dış zaman damgası olacak.
```
ON_KAYIT_FAZ14.md  SHA256 D4576B22171425D15A27AD2487B58F83A1EE864AA61319A7E66F30074DF84CC4
anahtar.jsonl      SHA256 74B7AE3CE7E72DB0B0A60CC5DE3108F1A390C73276862018DDFC9D3A8F11D082
secim.json         SHA256 7694C53CE2BBE6168EC35E896BDA564260528AD7230B11FBC49C42CC7FCE47DE
```

## Faz 17 parmak izleri (koşudan önce, 2026-10-13)
Kullanıcı bu satırları kendine e-postayla gönderecek. E-postanın zamanı dış zaman damgası olacak.
```nON_KAYIT_FAZ17_MUHURLU.md    SHA256 1AC8A88E0221BE00174A73F209BD97D81C886F0662D0040B7CD60463E1C57CC4
secim.json                   SHA256 8EF95D39B6346CCB3B728E055B4BE447B14D44EC29705CD4B54491C93E291A19
faz15.py                     SHA256 6A247242BD2285A6341F10F5CB066F9873A1ABCBE3DFA33B4590C5C6729DAF61
faz16.py                     SHA256 7CD1344B6D87D0926A0DCD18BC297E4C9A1FE4C6509C89743EABE62F5C6B78F3
faz5.py                      SHA256 BC18E0774A4F50C79FEC22C90DD943D76D836E5C83B25E4CED14CF4C6C87789C
faz4c.py                     SHA256 76544170BD7047FFF734ABF4DC65A4E26B8F24D0E7A19AA75641F38D68E01AC9
```

## Faz 18 parmak izleri (koşudan önce, 2026-10-13)
```nON_KAYIT_FAZ18_MUHURLU.md    SHA256 5A3F977037519C2A991338D3D6708422FCD0BAFD3B07ACF113EF16257C86E425
faz15.py                     SHA256 6A247242BD2285A6341F10F5CB066F9873A1ABCBE3DFA33B4590C5C6729DAF61
faz16.py                     SHA256 7CD1344B6D87D0926A0DCD18BC297E4C9A1FE4C6509C89743EABE62F5C6B78F3
faz5.py                      SHA256 BC18E0774A4F50C79FEC22C90DD943D76D836E5C83B25E4CED14CF4C6C87789C
faz4c.py                     SHA256 76544170BD7047FFF734ABF4DC65A4E26B8F24D0E7A19AA75641F38D68E01AC9
```
(Not: Yukarıdaki bloğun ilk satırındaki "```n" bir yazım hatası. İlk satır `ON_KAYIT_FAZ18_MUHURLU.md` olarak okunmalı.)

## Faz 19 parmak izleri (koşudan önce, 2026-10-13)
```
ON_KAYIT_FAZ19_MUHURLU.md     SHA256 BCF4768385B3BDACD10E069048336270590A3802DDC7D1594711BCF3C1C369D8
faz19.py                      SHA256 B2A2A066828C187061A4B4882FC0A34E331C0F9AB588770EA582F1C25986A575
faz18.py                      SHA256 929CE4BE0908C666B058F1671B76E9EF234A899B68E0838E9163F4C4D1CA9DB5
faz8.py                       SHA256 4C0BC841CA8162DB3FC68349965386EB212F7401060FBC38745CA9112C0BDA18
faz15.py                      SHA256 6A247242BD2285A6341F10F5CB066F9873A1ABCBE3DFA33B4590C5C6729DAF61
faz16.py                      SHA256 7CD1344B6D87D0926A0DCD18BC297E4C9A1FE4C6509C89743EABE62F5C6B78F3
faz5.py                       SHA256 BC18E0774A4F50C79FEC22C90DD943D76D836E5C83B25E4CED14CF4C6C87789C
faz4c.py                      SHA256 76544170BD7047FFF734ABF4DC65A4E26B8F24D0E7A19AA75641F38D68E01AC9
```
faz19.py'nin parmak izi, CUTOFF satırı "SET-BEFORE-FIRST-CALL" iken alındı. İlk çağrıdan önce yalnızca bu satır değişecek.

## Faz 19 defter düzeltmesi (denetim 2. tur, T2-3)
- Yukarıdaki "faz19.py'de ilk çağrıdan önce yalnızca CUTOFF satırı değişecek" cümlesi **yanlış.**
- İlk çağrıdan önce daraltma eki de `faz19.py`'yi değiştirdi: `RUN_DOCS`, `RUN_ARMS` ve `F` eklendi, analiz bunlara göre uyarlandı.
- İstemlere etkisi yok: istemler Faz 18 + çerçeve değişimiyle birebir aynı. Denetçi bunu doğruladı.
- Ekle birlikte alınan parmak izleri (ilk çağrıdan önce, kullanıcıya verildi):
```
ON_KAYIT_FAZ19_EK_MUHURLU.md  SHA256 1A43867925C2F67A714769238FF13B015D884B43E26EA2516F5B2A41C288D97E
faz19.py (CUTOFF ve ekle)     SHA256 19D28071BEFB64E6EF5C4E76820908212E9806B8BBE4AD0862C40FD948E3A8E6
```

## Faz 23 parmak izleri (koşudan önce, 2026-10-14)
```
ON_KAYIT_FAZ23_MUHURLU.md     SHA256 96459AFEF0B6A5036034A939D7229ED15675D36106402AB69A1B5540A4A05D23
faz23.py                      SHA256 67EDD0B4CA7A6E6D4648FA5E2128AF26B4C327D39F4F261090D058FB80DF75E1
faz4e.py                      SHA256 85E6AE6738F13E0E440C4B0769DFB9E3E09961849B0FDFF2E83A7F514CB869E8
faz4c.py                      SHA256 76544170BD7047FFF734ABF4DC65A4E26B8F24D0E7A19AA75641F38D68E01AC9
faz5.py                       SHA256 BC18E0774A4F50C79FEC22C90DD943D76D836E5C83B25E4CED14CF4C6C87789C
```
faz23.py'nin parmak izi, CUTOFF satırı "SET-BEFORE-FIRST-CALL" iken alındı. İlk çağrıdan önce yalnızca bu satır değişecek.
