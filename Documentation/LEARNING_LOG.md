# Öğrenme Defteri (Learning Log)

Gün gün ders notları ve trick'ler. Her önemli çalışma gününün sonunda
buraya derli toplu bir özet eklenir. Amaç: jargonsuz, parantezli
açıklamalarla kalıcı bir "çıraklık defteri" tutmak.

Format: her gün bir bölüm; her ders 3-6 satır — **ne oldu → neden →
kural/trick**.

---

## 2026-08-14 — İlk derleme, M1 kabulü, git kurtarma operasyonları

### 1. Guard (koruma kontrolü) sıralaması davranıştır, detay değildir
`RecordSectorBoundary` içinde iki guard vardı: "tur açık değil" ve
"tüm sektörler zaten kapandı". Tur bittiğinde `bLapOpen` false olduğu
için ikinci guard'a hiç ulaşılamıyordu — yani o kod **ölü koddu**
(hiçbir koşulda çalışmayan kod). Testin beklediği teşhis mesajı bu
yüzden hiç loglanmadı.
**Kural:** Ard arda gelen erken-çıkış kontrollerinde sıra, hangi hata
mesajının kazanacağını belirler. En **spesifik** teşhis en öne konur;
en genel olan en sona. Test yazarken de bunu bilinçli kodla: her guard
için o guard'ı tetikleyen ayrı bir senaryo yaz.

### 2. Savunmacı koşul güçlendirme
Guard'ı öne alınca yeni bir delik açıldı: hiç Configure edilmemiş
timer'da (`SectorCount == 0`) `Splits.Num() >= 0` her zaman doğru
olurdu. Çözüm: `SectorCount > 0 && Splits.Num() >= SectorCount`.
**Kural:** Bir koşulu taşıdığında, taşındığı yeni bağlamda hangi
durumların "yanlışlıkla" ona yakalanacağını düşün. Sınır değerleri
(0, boş dizi, ilk çağrı) her zaman kontrol listesinde olsun.

### 3. Unreal Live Coding derlemeyi kilitler
Editör açıkken `Build.bat` şu hatayı verir: "Unable to build while
Live Coding is active". Live Coding (editör içinden anlık kod yaması)
DLL'i kilitler.
**Trick:** Ya editörü kapat, ya editör içinden **Ctrl+Alt+F11** ile
derle. Dış terminal derlemesi + açık editör kombinasyonu çalışmaz.

### 4. `git push` reddi: "fetch first" paniğe gerek yok
Remote'a (uzak depo, GitHub'daki kopya) başka bir kanaldan commit
girmişse push reddedilir. Bu bir hata değil, koruma: senin görmediğin
işi ezmeni engelliyor.
**Akış:** `git pull --rebase` (kendi commit'ini uzaktakilerin üstüne
yeniden oynatır) → tekrar push. Rebase sonrası commit'in **hash'i
(parmak izi) değişir** — bizde `25aa048` → `dbfb5d4` oldu. Eski hash'i
arayan bulamaz; commit mesajıyla doğrula.

### 5. LFS filtrelerini tek komutluk kapatma trick'i
OPEN-076-A yüzünden 4 PNG sürekli "modified" görünüyor ve rebase'i
blokluyor. Kalıcı çözüm sonraya; geçici çözüm, git'e o komut için LFS
filtrelerini (dosyaları işaretçiye çevirip geri açan katman) kapattırmak:
```
git -c filter.lfs.smudge= -c filter.lfs.clean= -c filter.lfs.process= -c filter.lfs.required=false <komut>
```
**Kural:** `-c ayar=değer` git'e tek seferlik yapılandırma verir;
global config'e dokunmaz, iz bırakmaz.

### 6. PowerShell tırnak tuzağı: `stash@{0}`
PowerShell `@{...}` yazımını hashtable (anahtar-değer sözlüğü) sanır ve
git'e bozuk argüman gider — bizde `error: unknown switch 'e'` çıktı.
**Kural:** PowerShell'de süslü parantezli git referanslarını **her zaman
tek tırnakla** yaz: `'stash@{0}'`, `'HEAD@{1}'`.

### 7. Drop edilen stash kayıp değildir (dangling commit kurtarma)
`git stash drop` çalıştı ama içindeki değişiklik daha geri alınmamıştı.
Panik yok: stash aslında gizli bir commit'tir; drop mesajı SHA'sını
yazar (`Dropped ... (d9fdbfe...)`). Bu commit "dangling" (hiçbir dala
bağlı olmayan ama nesne deposunda duran) halde, çöp toplayıcı çalışana
kadar (~2 hafta) erişilebilir.
**Kurtarma:** `git checkout <SHA> -- <dosya>` (cımbız checkout: tüm
commit'e geçmeden tek dosyayı çekmek). Not: bu komut dosyayı stage'ler;
`git restore --staged <dosya>` ile indirilir.

### 8. Süreç dersi: iki yazar, tek main
Bu projede asistan GitHub API üzerinden doğrudan `main`'e yazıyor,
geliştirici lokalden push ediyor. Çakışma kaçınılmaz.
**Kural:** API tarafı `main`'e yazdıktan sonra, lokal her push öncesi
`git pull --rebase` yapılır (LFS trick'iyle birlikte). Sıra:
lokal push biter → API yazar → lokal pull → lokal push.
