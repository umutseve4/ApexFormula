# DECISION LOG - VOL 16

Onceki cilt: DECISION_LOG_VOL15.md (D-079 .. D-086, DONDURULDU)

---

## D-087 - M5.2 KAPANDI: Physics Asset 5 gövdeye yeniden inşa edildi (hibrit GUI + UE Python)

**Tarih:** 2026-08-15
**Durum:** KAPANDI (dogrulandi)
**Ilgili:** D-086 (baseline tespiti), OPEN yok

### Karar
`AF_Vehicle_Proto_PhysicsAsset` D-086 hedef yerlesimine getirildi ve dogrulandi:

| Body | Kemik | Primitif | Boyut |
|---|---|---|---|
| 1 | AF_Chassis | KBoxElem | X=560, Y=194, Z=94 (tam genislik) |
| 2 | AF_Wheel_FL | KSphereElem | r=36 |
| 3 | AF_Wheel_FR | KSphereElem | r=36 |
| 4 | AF_Wheel_RL | KSphereElem | r=38 |
| 5 | AF_Wheel_RR | KSphereElem | r=38 |

Constraint: 0 (D-086 geregi kabul; Chaos artikulasyonu M6+).
AF_Root / AF_Steering / AF_Suspension_* uzerinde body YOK (raycast suspansiyon plani).

### Kanit
- UE Python cikti: `AF_Wheel_* : Sphere r=... yazildi` x4, `AF_Chassis : box=1`,
  `SONUC : PASS - chassis Box + 4 tekerlek Sphere kaydedildi`.
- `LogSavePackage: Moving output files for package: /Game/vehicle/AF_Vehicle_Proto_PhysicsAsset`
  (asset diske kaydedildi, 2026-08-15 ~02:41 UTC).
- Script: `BlenderPipeline/tools/fix_physasset.py` (repo'da).

### Yontem ve kesifler (UE 5.8.1 Python API sinirlari)
Salt-script cozum DENENDI ve teknik olarak imkansiz cikti; kanit zinciri:
1. `unreal.SkeletalBodySetup` modul attribute'u olarak yok (AttributeError).
   Cozum: `unreal.load_class(None, '/Script/Engine.SkeletalBodySetup')` ile sinif yuklendi.
2. `SkeletalBodySetup.bone_name` Python'dan salt-okunur
   ("Property 'BoneName' ... is read-only").
3. `PhysicsAsset.skeletal_body_setups` property'si Python yuzeyinde HIC yok
   (class docstring Editor Properties listesinde bulunmuyor -> derleme zamaninda kapali).
Sonuc: yeni body YARATMAK script ile imkansiz; var olan body'yi DEGISTIRMEK mumkun.

**Hibrit cozum (kabul edilen):**
- GUI (kullanicinin ekraninda dogrulanan tek menu): Skeleton Tree'de 4 tekerlek kemigi
  secilip "Add Bodies" ile bos body'ler yaratildi.
- UE Python: subobject yolu (`Paket.Asset:SkeletalBodySetup_N`) ile her body'nin
  `agg_geom`'u kesin sayisal degerlerle yeniden yazildi ve asset kaydedildi.

### Post-mortem: script aktarim bozulmasi
Ilk script kosusu SyntaxError ile dustu: sohbet arayuzu kopyalama sirasinda
`dims[0]` ifadesine link enjekte etti. Onlem (kalici politika):
- Teslim edilen her PowerShell blogu, yazdigi .py dosyasini `http|citation`
  desenleriyle tarayip PASS/FAIL basar (self-validating delivery).
- Riskli `[i](...)` bitisik desenlerinden kacinilir (tuple unpacking / dict tercih).

### Kalici politika notu (D-086 sonrasi yasanan GUI turlarina istinaden)
SCRIPT-FIRST kurali yururlukte: editor isleri varsayilan olarak UE Python ile yapilir;
GUI yalnizca (a) script yolu kanitli kapaliysa VE (b) menu/buton kullanicinin guncel
ekran goruntusunde/beyaninda birebir dogrulanmissa tarif edilir. Ayni yaklasim 3. kez
denenmez; 2. FAIL'de yontem degistirilir.

### Sonraki adim
- M5.3: sayisal kabul (dingil mesafesi 360 +-1, boy 560 +-1, +X ileri, +Z yukari).
- LFS commit: `Unreal/Content/Vehicle/AF_Vehicle_Proto_PhysicsAsset.uasset` (bu kayitla eszamanli).

### Zeyl (2026-08-15 ~02:45 UTC): push dogrulandi
- Commit `4e316eb` push edildi (`feat(physics): D-087 - rebuild PhysAsset to 5 bodies ...`).
- LFS upload: 1 obje, 11 KB; pointer dogrulandi
  (`version https://git-lfs.github.com/spec/v1` — dosya icerigi pointer, binary degil).
- M5.2 boylece %100 kapali: uretildi + dogrulandi + versiyonlandi.

---

## D-088 - M5.3 protokolu: sayisal kabul (paste-only)

**Tarih:** 2026-08-15
**Durum:** ACIK (script repoda hazir, kosum bekliyor)
**Ilgili:** D-087 (M5.2 kapanisi), D-078 (olcum protokolu mirasi)

### Karar
M5.3 kabulu TEK UE Python scripti ile yapilir; GUI adimi SIFIR.
Script: `BlenderPipeline/tools/accept_m53.py` (commit `0d41efe` ile repoda).

Kabul kriterleri (hepsi ayni kosumda PASS olmali):

| # | Kontrol | Hedef | Tolerans |
|---|---|---|---|
| A | Dingil mesafesi (FL-RL ve FR-RR, X ekseni) | 360 cm | +-1 cm |
| B | Arac boyu (imported bounds X) | 560 cm | +-5 cm (bounds kanat/govde tasmasi icerebilir) |
| C | Yon: +X ileri | on tekerlek X > arka tekerlek X | bool |
| D | Yon: +Z yukari | sasi merkez Z > tekerlek ortalama Z | bool |

NOT (D-089): D kontrolu tasarim hatasiydi; revize hali icin D-089'a bakin.

### Yontem
- Mesh `/Game/Vehicle/AF_Vehicle_Proto` yuklenir; gecici `SkeletalMeshActor`
  spawn edilip kemik dunya konumlari `get_socket_location` ile okunur
  (bind-pose sorgusu icin en garantili Python yolu; aktor sonda destroy edilir).
- Bounds `get_imported_bounds()` ile okunur.
- Cikti `===== OTOMATIK KONTROL =====` altinda kontrol basina PASS/FAIL + tek satir SONUC.

### Kosum (kullanici tek satir yapistirir, once git pull)
```
py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/accept_m53.py"
```

### Kabul
- 5 kontrol de PASS -> M5.3 KAPANDI, D-088 guncellenir, M5.4 (Chaos Vehicle kurulumu) acilir.
- Herhangi FAIL -> sapma D-088 altina islenir; duzeltme Blender kaynak tarafinda yapilir
  (UE'de elle tasima YASAK — pipeline butunlugu).

---

## D-089 - M5.3 ILK KOSUM FAIL: 100x olcek kaybi kok nedeni + config v0B.1.3 + D kontrolu revizyonu

**Tarih:** 2026-08-15
**Durum:** DUZELTME PUSH EDILDI (yeniden export + reimport + kabul kosumu bekliyor)
**Ilgili:** D-088 (kabul protokolu), D-084 (legacy FBX importer karari), OPEN-080-A (onceki olcek vakasi)

### Bulgu (kanit: 2026-08-15 accept_m53.py ilk kosumu)
Tum lineer olculer tam 1/100 geldi:
- B: bounds X = 5.60 cm (hedef 560) -> FAIL
- A: dingil 3.60 cm (hedef 360) -> FAIL x2
- C: +X ileri PASS (yon olcekten bagimsiz)
- D: FAIL (asagida ayri ele alindi — bagimsiz tasarim hatasi)

### Kok neden (olcek)
Config v0B.1.2 `apply_scale_options='FBX_SCALE_UNITS'` kullaniyordu.
SCALE_UNITS m->cm x100 donusumunu SADECE FBX birim METADATA'sina yazar;
vertex/kemik verisi metre olarak kalir. UE'nin legacy FBX importeri (D-084 geregi
aktif) bu metadata'yi varsayilan ayarlarla DIKKATE ALMAZ -> her sey 1/100 gelir.
OPEN-080-A'daki SCALE_ALL denemesi ise tersine root kemige scale=100 basiyordu.
Uc secenegin davranis matrisi:

| apply_scale_options | Vertex verisi | Root scale | Legacy importer sonucu |
|---|---|---|---|
| FBX_SCALE_ALL | cm (x100 uygulanir) | 100 (kirli) | dogru boy ama kirli iskelet (OPEN-080-A) |
| FBX_SCALE_UNITS | m (degismez) | 1 | 1/100 kucuk (bu vaka) |
| FBX_SCALE_NONE + scene.unit_settings dogru | cm (veriye islenmis) | 1 (beklenen) | dogru boy + temiz iskelet (hedef) |

### Duzeltme
- Config v0B.1.3: `apply_scale_options='FBX_SCALE_NONE'`; self_check bu degeri
  D-089 referansiyla zorunlu kilar. Commit: `3a68ac1`, byte-dogrulama duzeltmesi `d21ddce`.
- Yeniden export headless: `blender --background --python BlenderPipeline/scripts/af_smoke_test.py`
  (sahne sifirdan uretilir, .blend gerekmez).

### Post-mortem: push aktarim bozulmasi (2. vaka)
`3a68ac1` push'unda icerik bellekten yeniden yazildi ve `__main__` print'ine
20 baytlik walrus artefakti sizdi (`OWNED_COLLISIONS := OWNED_COLLECTIONS`).
Tespit: lokal git blob SHA (`hashlib.sha1(b'blob %d\0' % len + data)`) ile
GitHub'in dondurdugu blob SHA karsilastirildi; tek fark bu satirdi. `d21ddce`
ile duzeltildi, donen blob SHA `376d31dd...` lokal ile birebir esledi.
KALICI POLITIKA: repo'ya iceriik push'lanirken asla bellekten yeniden yazma;
push oncesi/sonrasi blob SHA esitligi kanit olarak zorunlu.

### D kontrolu revizyonu (bagimsiz tasarim hatasi)
Eski D: "sasi merkez Z > tekerlek ortalama Z". Tasarimda sasi kemigi origin'i
chassis_top/2 = 0.28 m = 28 cm'dedir; tekerlek merkezleri 36/38 cm. Yani DOGRU
veride bile D gecemezdi. Revize D: sasi kemigi Z = 28 +- 1 cm (Z > 0 oldugu
icin +Z yukari kanitini da icerir). Commit: `3146f70`.

### Kabul (D-088 guncellenmis kriterlerle)
1. Yeniden export (smoke test 7 asama PASS, config 0B.1.3 dogrulanir).
2. UE reimport (script ile, AssetImportTask).
3. `accept_m53.py` yeniden kosum: A/B/C/D hepsi PASS -> M5.3 KAPANDI.
4. Reimport sonrasi ek dogrulama: iskelet root scale (1,1,1) VE PhysAsset'te
   5 body'nin korundugu (reimport body'leri sifirlayabilir; gerekirse
   `fix_physasset.py` geometri kosumu tekrarlanir — body'ler mevcutsa salt-script yeter).

---

## D-090 - M5.3 IKINCI KOSUM: SCALE_NONE ile boy DUZELDI, root scale=100 kaldi -> export-time cm bake (v0B.1.4)

**Tarih:** 2026-08-15
**Durum:** DUZELTME PUSH EDILDI (yeniden export + reimport + kabul kosumu bekliyor)
**Ilgili:** D-089 (SCALE_NONE karari), D-088 (kabul protokolu), OPEN-080-A (root scale=100 ilk vaka)

### Bulgu (kanit: 2026-08-15 reimport_vehicle.py kosumu, config v0B.1.3)
- BOUNDS : PASS - X=560.00 Y=194.00 Z=94.00 cm (tam hedef; 1/100 sorunu bitti)
- PHYSA  : PASS - 5 body reimport'u sag atlatti (fix_physasset tekrar gerekmedi)
- ROOT   : FAIL - AF_Root scale=(100,100,100) (hedef 1,1,1)

### Kok neden
Sahne METRE cinsinden kurulu (scale_length=1.0). SCALE_NONE'da exporter veriyi
degistirmez ama m->cm x100 birim donusumunu yine de dosyaya node donusumu olarak
yazmak zorunda kalir; UE legacy importeri bu x100'u root kemigin referans-poz
scale'ine katlar. Yani D-089 matrisindeki "SCALE_NONE + scene dogru" satirinin
on kosulu eksikti: sahne verisi zaten cm olmali ki donusturulecek bir sey kalmasin.

### Duzeltme: export aninda cm bake (v0B.1.4, iki commit)
- `af_pipeline_config.py` -> `PIPELINE_VERSION=0B.1.4` (commit `7a86eb0`, blob dogrulandi).
- `af_export.py` -> `bake_cm()` / `unbake_cm()` + `export_all()` icinde try/finally
  (commit `d11a03b`, blob `81abb645...` lokal ile birebir).
- Mekanizma: export'tan hemen once tum export seti icin konumlar + mesh/armature
  DATA'si x100 olceklenir (obj.scale (1,1,1) kalir), `scale_length` 0.01'e cekilir;
  efektif birim carpani 100 x 0.01 = 1.0 -> dosyada tasinacak donusum kalmaz.
  Export bitince finally blogu sahneyi metreye geri alir ve `scale_length`'i
  config sabitine esitler (float kaymasina karsi).
- 2.-FAIL kurali geregi 4. bir `apply_scale_options` denemesi YAPILMADI;
  yontem degistirildi (exporter secenegi yerine veri bake'i).

### Olcek vakalari ozet matrisi (kapanis referansi)
| Deneme | Sonuc |
|---|---|
| FBX_SCALE_ALL (OPEN-080-A) | boy dogru, root=100 (kirli) |
| FBX_SCALE_UNITS (D-089) | 1/100 kucuk |
| FBX_SCALE_NONE (bu kosum) | boy dogru, root=100 |
| SCALE_NONE + cm bake (v0B.1.4) | beklenen: boy dogru + root (1,1,1) - kosum bekliyor |

### Kabul
1. Headless smoke: 7 asama PASS, `pipeline version 0B.1.4`, config hash `933a11f6292ec2b5`.
2. `reimport_vehicle.py`: BOUNDS PASS + ROOT PASS (1,1,1) + PHYSA PASS (5 body).
3. `accept_m53.py`: A/B/C/D hepsi PASS -> M5.3 KAPANDI; D-088/089/090 kapanir.

### Yedek plan (bu da FAIL olursa)
Blender tarafi denemesi biter; UE tarafina gecilir: import script'inde
`ImportUniformScale` / importer birim ayarlariyla duzeltme (yontem degisikligi,
ayni yaklasimin 3. denemesi degil).

---

## D-091 - M5.3 KAPANDI: v0B.1.4 dogrulandi, sayisal kabul 5/5 PASS

**Tarih:** 2026-08-15
**Durum:** KAPALI
**Ilgili:** D-088 (protokol), D-089 (SCALE_NONE + D-kriteri revizyonu), D-090 (cm bake)

### Sonuc

M5.3 sayisal kabul kriterleri, v0B.1.4 (config hash 933a11f6292ec2b5) ile
uretilen FBX'in (217292 B) yeniden import'u sonrasi **5/5 PASS** ile karsilandi.

### Kosum kaniti (Umut'un makinesi, UE 5.8.1)

1. **Smoke (Blender headless):** 6/6 stage PASS, failed 0. FBX 217292 B
   (v0B.1.3'te 219756 B idi; cm bake sonrasi fark normal).
2. **reimport_vehicle.py:**
   - BOUNDS : PASS - X=560.00 Y=194.00 Z=94.00 cm
   - ROOT   : PASS - AF_Root scale=(1.000, 1.000, 1.000)
   - PHYSA  : PASS - 5 body (sasi Box + 4 teker Sphere) reimport'u sagladi
3. **accept_m53.py (5/5):**
   - B-BOY        : PASS - bounds X = 560.00 cm (hedef 560 +- 5)
   - A-DINGIL-SOL : PASS - FL-RL X farki = 360.00 cm (hedef 360 +- 1)
   - A-DINGIL-SAG : PASS - FR-RR X farki = 360.00 cm (hedef 360 +- 1)
   - C-ILERI+X    : PASS - on X (180/180) > arka X (-180/-180)
   - D-SASI-Z     : PASS - sasi Z = 28.00 cm (hedef 28 +- 1; D-089 revizyonu)
   - Bilgi: iz genisligi on=160.00 arka=154.00 cm; teker Z on=36 arka=38 cm.

### Kapanan kayitlar

- **D-088:** protokoldeki "5 kontrol de PASS -> M5.3 KAPANDI" kosulu saglandi. KAPALI.
- **D-089:** SCALE_NONE + cm bake kombinasyonu dogru cozum olarak dogrulandi;
  scale-secenek matrisindeki v0B.1.4 satiri "dogrulandi (5/5)" statusune gecti. KAPALI.
- **D-090:** "kosum bekliyor" notu kalkti; export-time cm bake empirik olarak
  dogrulandi (root scale 1,1,1). KAPALI.
- **OPEN-080-A olcek sagasi:** x0.01 (D-085) -> x100 (D-089) -> x1 (D-090/091).
  Tamamen kapandi; bir daha acilmasi icin yeni kanit gerekir.

### Ertelenen is

- Documentation/MILESTONE_PLAN.md durum tablosu ("3-12 Not started" satiri)
  guncellenmedi. Gerekce: D-089 transfer-butunlugu politikasi (push edilmis
  icerik bellekten yeniden yazilmaz; blob-sha esitligi sart) ve M5'in butunuyle
  henuz acik olmasi. Tablo, M5 tamamen kapandiginda tek seferde guncellenecek.

### Sonraki adim

- **M5.4 - Chaos Vehicle entegrasyonu.** Plan ayri kayit olarak acilacak (D-092):
  ChaosVehiclesPlugin, WheeledVehiclePawn BP (AF_Vehicle_Proto mesh + PhysAsset),
  AF_Wheel_FL/FR/RL/RR teker sinif eslemesi, tork egrisi, Enhanced Input,
  GameMode + test haritasi, surus testi kabulu. Script-first (UE Python) esas.
