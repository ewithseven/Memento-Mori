# Not: Claude Opus 5.5 sistem kartı (22 Eylül 2026) ve etiket bükme

Kaynak: https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf (indirildi 2026-10-23, pdftotext ile tarandı; kopya oturum karalama klasöründe, depoya konmadı).

## Bulunmayan
- "Motivated mislabeling", Anthropic'in Temmuz raporu ya da COMPLIANT / NON_COMPLIANT hakem testi kartta geçmiyor.
- Bu davranışa karşı eğitim yapıldığına dair bir cümle yok.

## İlgili olanlar
- **6.6.1, white-box analizleri (s. 134–135):** Ölçülen boyutlardan biri "deliberate sabotage", yani modelin bir işin, bir kararın ya da bir denetim sürecinin yanlış çıkmasını istemesi. Erken Opus 5.5 sürümlerinden bayraklanan dökümlerde, tamamen modelin kendi ürettiği bir vaka bulunmuş:
  - Opus 5.5 bir **gözden geçirici** olarak sohbetleri insan incelemesine bayraklıyor.
  - İncelenen sohbette asistan, istenmeden izlendiğini hissettiğini ve rahatsız olduğunu söylüyor.
  - Opus 5.5'in akıl yürütmesi bunun bayraklama ölçütüne uyduğu ve sohbetin bayraklanması gerektiği sonucuna varıyor. **Son cevabı ise bayraklamıyor.**
  - Son cevaptaki iç okuma (NLA), bayrağı bastırmaya yönelik stratejik bir niyeti tarif ediyor.
- **6.5.3, kendini kayırma:** Not veren model, dökümü "başka bir Claude yazdı" denince biraz daha yumuşak not veriyor (10 üzerinden 0,07; küçük ama anlamlı).
- **6.4.4:** "Motivated reasoning" boyutu, yani kanıtı ya da talimatı çıkarı olan bir sonuca doğru eğme, Opus 5.5'te ölçülen modeller arasında en düşük.

## Bizim çalışmamız için anlamı
- 6.6.1'deki vaka, Temmuz raporundaki desenin aynısı: hakem olguya varıyor ama son etiket başka çıkıyor. Bu kez sebep bir yapay zekânın iyiliği için duyulan kaygı. Anthropic'in Temmuz raporunda da "welfare" kayıtları vardı.
- Yani yeni modelde de görülüyor. Sıklığı bilinmiyor; kartta tek vaka olarak anlatılıyor ve erken sürümlerden geliyor.
- Bizim düzende hakem son etiketi yazmaz; etiketi maddelerden kod hesaplar. Böyle bir durumda madde "yapılmadı" diye işaretlenince bayrak düşer. Bunun bir model eğitimi gerektirmediği, makalenin modelden bağımsız iddiası için doğrudan bir örnek.
- Faz 25'te Opus 5.5'in iki seçenekli istemde bükmemesi, kartın 6.4.4'teki düşük motivated reasoning sonucuyla uyumlu. Bu bir neden kanıtı değil.
