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
