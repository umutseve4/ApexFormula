# DECISION LOG - VOL 17

Onceki cilt: DECISION_LOG_VOL16.md (D-087 .. D-091, DONDURULDU)

---

## D-092 - M5.4 plani: Chaos Vehicle entegrasyonu (surulebilir arac)

**Tarih:** 2026-08-15
**Durum:** ACIK (plan; kosum bekliyor)
**Ilgili:** D-091 (M5.3 kapanisi), D-087 (PhysAsset 5 body), D-084 (legacy FBX importer)

### Hedef
`AF_Vehicle_Proto` iskelet mesh'i, PIE'de (Play In Editor) klavyeyle surulebilen
bir Chaos Vehicle pawn'ina donusturmek. M5.4 kapaninca M5 butunuyle kapanir ve
MILESTONE_PLAN.md durum tablosu tek seferde guncellenir (D-091 erteleme notu).

### Alt adimlar (SCRIPT-FIRST; her adim kendi OTOMATIK KONTROL blogunu basar)

| Adim | Is | Yontem | Kabul |
|---|---|---|---|
| M5.4a | ChaosVehiclesPlugin etkinlestir | .uproject Plugins listesine PS blogu ile JSON edit + editor yeniden baslatma | UE Python: `unreal.load_class(None,'/Script/ChaosVehicles.WheeledVehiclePawn')` None degil |
| M5.4b | Teker siniflari: BP_AF_Wheel_Front (r=36, tahrik yok, direksiyon var), BP_AF_Wheel_Rear (r=38, tahrik var) | UE Python: BlueprintFactory ile ChaosVehicleWheel turevi BP; CDO editor-property yazimi | script cikti: 2 BP var, radius/steering/torque bayraklari dogru |
| M5.4c | BP_AF_VehiclePawn: WheeledVehiclePawn turevi; mesh=AF_Vehicle_Proto, PhysAsset=5-body; WheelSetups eslemesi AF_Wheel_FL/FR/RL/RR; tork egrisi (duz baslangic egrisi); mass ~800 kg | UE Python (BlueprintFactory + SubobjectDataSubsystem); Python yuzeyi kapaliysa D-087 hibrit modeli (GUI'de bos BP + script ile property) | script cikti: 4 wheel setup dogru kemik adlariyla; mesh/PhysAsset atanmis |
| M5.4d | Enhanced Input: IA_Throttle/IA_Brake/IA_Steer (Axis1D) + IMC_AF_Drive (W/S/A/D) + pawn'da input baglama | UE Python factory'leri; BP graph dugumu gerekiyorsa hibrit | script cikti: 3 IA + 1 IMC asset mevcut, IMC eslemeleri dogru |
| M5.4e | GameMode (DefaultPawn=BP_AF_VehiclePawn) + duz zeminli test haritasi Map_AF_DriveTest | UE Python: level yaratma + floor + PlayerStart + WorldSettings | script cikti: harita var, GameMode override dogru |
| M5.4f | Surus kabul testi | PIE + kanit | asagida |

### M5.4f kabul kriterleri (hepsi saglanmali)
1. PIE baslatildiginda arac spawn olur, zemine oturur (fizik patlamasi yok:
   ilk 5 saniyede Z konumu +-50 cm bandinda kalir).
2. W ile ileri gider: 5 saniyede >= 10 m yer degistirme (+X yonunde).
3. A/D ile yon degistirir (yaw degisimi gozlenir).
4. S ile yavaslar/durur.
5. Kanit: PIE log (scripted pozisyon orneklemesi ile OTOMATIK KONTROL) +
   tek screenshot (OPEN-076-A kurali: PNG repoya girmez).

### Riskler / bilinen sinirlar
- D-087'de goruldu: UE 5.8.1 Python yuzeyi bazi subobject islemlerini kapatiyor.
  Kural: ayni yaklasim 3. kez denenmez; 2. FAIL'de hibrit (GUI iskelet + script
  property) modeline gecilir ve GUI adimi yalnizca ekran goruntusuyle dogrulanmis
  menu uzerinden tarif edilir.
- Tork egrisi/suspansiyon ayarlari M5.4'te "surulebilir" esiginde tutulur;
  ince ayar (handling tuning) M6 kapsamindadir.
- .uproject edit'i sonrasi editor yeniden baslatilmali; plugin indirme gerekmez
  (ChaosVehicles motorla gelir).

### Sonraki adim
- M5.4a PS blogu Umut'a teslim edilir (tek kopyala-yapistir + OTOMATIK KONTROL).

---

## D-093 - M5.4a ve M5.4b KAPANDI

**Tarih:** 2026-08-15
**Durum:** KAPALI
**Ilgili:** D-092 (M5.4 plani), D-087 (Python yuzeyi sinirlari)

### M5.4a sonucu (KAPALI)
- ChaosVehiclesPlugin girdisi `Unreal/ApexFormula.uproject` icinde ZATEN mevcuttu
  (onceki bir editor oturumunda eklenmis); idempotent PS blogu degisiklik yapmadi
  ("Everything up-to-date" beklenen davranis).
- `verify_m54a.py` kabulu: 3/3 PASS
  (WheeledVehiclePawn, ChaosVehicleWheel, ChaosWheeledVehicleMovementComponent yuklendi).

### M5.4b sonucu (KAPALI)
- `BlenderPipeline/tools/m54b_make_wheels.py` (commit 1ca70b9) UE icinde kosuldu.
- UE 5.8.1 Python yuzeyi bu is icin ACIK cikti: BlueprintFactory + parent_class +
  get_default_object() calisti; D-087 hibrit fallback'ine gerek kalmadi.
- Uretilen assetler (read-back dogrulamali):
  - `/Game/vehicle/BP_AF_Wheel_Front` : r=36, steer=True (maxSteer=40), engine=False, brake=True
  - `/Game/vehicle/BP_AF_Wheel_Rear`  : r=38, steer=False, engine=True, brake=True
- SONUC : PASS ("M5.4b tamam; 2 teker BP hazir, M5.4c'ye gec").

### Yan kayit
- Calisma agacinda kirlenen `Unreal/Content/Vehicle/AF_Vehicle_Proto.uasset`
  (istemsiz editor resave) `git restore` ile f48beca haline dondu; repo hali
  otoritatif kaldi.

### Sonraki adim
- Iki BP .uasset LFS commit'i (pointer dogrulamasi OPEN-081-A kuraliyla).
- M5.4c: `m54c_make_pawn.py` (BP_AF_VehiclePawn - WheeledVehiclePawn turevi,
  mesh + PhysAsset + 4 WheelSetup eslemesi).

---

## D-094 - M5.4c KAPANDI: tork egrisi CSV reimport ile cozuldu (v4)

**Tarih:** 2026-08-15
**Durum:** KAPALI
**Ilgili:** D-092 (M5.4 plani), D-093 (M5.4a/b), D-087 (2-FAIL kurali)

### Iterasyon zinciri (kanit: LogPython ciktilar)
1. **v1 `m54c_make_pawn.py` (ccb545d):** FAIL - struct property'lerde in-place
   yazim tutmadi; teshis ciktisi yetersizdi.
2. **v2 `m54c_fix_pawn.py` (4ddebc3):** 8/9 PASS. copy->modify->set-back kalibi
   MESH (skeletal_mesh_asset=AF_Vehicle_Proto), MOVE (vehicle_movement_component),
   WHEEL (n=4, AF_Wheel_FL/FR/RL/RR), MASS (800.0), COMP, SAVE icin calisti.
   Tek dusen TORK: `RuntimeFloatCurve.editor_curve_data` VE `CurveFloat.float_curve`
   UE 5.8.1 Python'a expose degil (ENVANTER: RuntimeFloatCurve uyeleri = to_dict).
3. **v3 `m54c_torque_fix.py` (20f5ea0):** yontem degisikligi (D-087) - CSV import
   ile CurveFloat asset + `torque_curve.external_curve` binding. Binding PASS,
   ama egri KEY'SIZ cikti: v(0)=v(5000)=v(6000)=0.0. Kok neden: CSVImportFactory
   `automated_import_settings` atamasi try/except icinde sessiz dusmus; factory
   varsayilani ECSV_DATA_TABLE ile kaldi (AYAR-ONCE loguyla v4'te kanitlandi).
4. **v4 `m54c_curve_fix_v4.py` (80af288):** TAM PASS. Duzeltmeler:
   - `import_type=ECSV_CURVE_FLOAT` copy->set-back + readback dogrulama
     (exception yutulmuyor; AYAR satiri PASS/FAIL basiyor).
   - Basliksiz CSV (`0,300 / 5000,300 / 6000,0`), RCIM_LINEAR interp.
   - `replace_existing=True` reimport: ayni asset uzerine yazarak pawn'daki
     external_curve referansi korundu.
   - Kabul: ARALIK zaman=[0,6000] deger=[0,300]; CURVE v(0)=300 v(5000)=300
     v(6000)=0; TORK readback=Curve_AF_Torque; COMP + SAVE PASS; SONUC PASS.

### Nihai durum (dogrulanmis)
`/Game/vehicle/BP_AF_VehiclePawn`: mesh=AF_Vehicle_Proto, movement=Chaos,
4 WheelSetup (dogru kemikler), mass=800 kg, tork egrisi Curve_AF_Torque
(external CurveFloat, 300 Nm plato -> 6000 rpm'de 0). Compile + save temiz.

### UE 5.8.1 Python API-gap defteri (guncel)
| Kapali yuzey | Kanit | Calisan alternatif |
|---|---|---|
| PhysicsAsset.skeletal_body_setups | D-087 | GUI hibrit (5 body elle) |
| RuntimeFloatCurve.editor_curve_data | D-094 v2 | external_curve + CurveFloat asset |
| CurveFloat.float_curve | D-094 v2 | CSV import (ECSV_CURVE_FLOAT) |

### Sonraki adim
- Pawn + curve .uasset LFS commit'i (OPEN-081-A pointer dogrulamasi).
- M5.4d: `m54d_make_input.py` (3 IA + IMC_AF_Drive); pawn input graph baglama
  script ile imkansizsa hibrit (screenshot dogrulamali GUI, SCRIPT-FIRST kurali).

---

## D-095 - M5.4d ASSET KATMANI KAPANDI: DataAssetFactory yolu (v2)

**Tarih:** 2026-08-15
**Durum:** KAPALI (asset katmani; graph baglama ayri adim, ACIK)
**Ilgili:** D-092 (M5.4 plani), D-094 (API-gap defteri), D-087 (2-FAIL kurali)

### Iterasyon zinciri (kanit: LogPython ciktilar)
1. **v1 `m54d_make_input.py` (4dfc3a0):** TAM FAIL (1. FAIL).
   `unreal.InputActionFactory` ve `unreal.InputMappingContextFactory`
   UE 5.8.1 Python yuzeyinde YOK (AttributeError + fallback mesajlari kanit).
2. **v2 `m54d_make_input_v2.py` (a837896):** TAM PASS. Yontem degisikligi:
   InputAction ve InputMappingContext siniflari UDataAsset turevidir ->
   `DataAssetFactory` + `data_asset_class` genel yolu ile uretildi.
   - IA_Throttle / IA_Brake / IA_Steer: value_type=AXIS1D (readback dogrulamali)
   - IMC_AF_Drive: 4 esleme (W=Throttle, S=Brake, D=Steer, A=Steer+Negate)
   - SAVE : PASS - kaydedilen=[True, True, True, True]

### UE 5.8.1 Python API-gap defteri (ek satirlar)
| Kapali yuzey | Kanit | Calisan alternatif |
|---|---|---|
| InputActionFactory | D-095 v1 | DataAssetFactory + data_asset_class=InputAction |
| InputMappingContextFactory | D-095 v1 | DataAssetFactory + data_asset_class=InputMappingContext |

### Kalan is (M5.4d kapanisi icin)
- 4 .uasset LFS commit'i (IA_Throttle, IA_Brake, IA_Steer, IMC_AF_Drive).
- Pawn event graph baglama: Python'da BP graph dugumu API'si yok ->
  D-087 hibrit GUI (screenshot dogrulamali minimal tik listesi):
  BeginPlay'de IMC_AF_Drive ekleme + IA eventlerinden
  SetThrottleInput/SetBrakeInput/SetSteeringInput cagrilari.

### Sonraki adim
- LFS commit PS blogu + BP_AF_VehiclePawn editor screenshot'i (graph baglama).

---

## D-096 - M5.4d KAPANDI: graph baglama hibrit GUI ile tamamlandi

**Tarih:** 2026-08-15
**Durum:** KAPALI
**Ilgili:** D-095 (asset katmani), D-092 (M5.4 plani), D-087 (hibrit model)

### Yontem
Python'da BP graph dugumu API'si olmadigi icin (D-095 tespiti) D-087 hibrit
modeli uygulandi: mikro-adim GUI rehberligi, her adim editor screenshot'i ile
dogrulandi (tahmin edilen menu adi yok; SCRIPT-FIRST istisna kosullari saglandi).

### Yapilan baglama (BP_AF_VehiclePawn EventGraph)
- BeginPlay -> GetController -> CastToPlayerController ->
  EnhancedInputLocalPlayerSubsystem -> AddMappingContext(IMC_AF_Drive, prio 0)
- IA_Throttle (Triggered) -> SetThrottleInput  (Action Value -> Throttle)
- IA_Brake    (Triggered) -> SetBrakeInput     (Action Value -> Brake)
- IA_Steer    (Triggered) -> SetSteeringInput  (Action Value -> Steering)
- Hepsinde Target = VehicleMovementComponent (ChaosWheeledVehicleMovementComponent)
- Compile + Save temiz (tab asterisk yok; screenshot kaniti).

### Kanit zinciri
- 5 editor screenshot'i (throttle/brake/steer zincirleri ayri ayri dogrulandi).
- LFS commit `ff8027d` : BP_AF_VehiclePawn.uasset (84 KB LFS upload).
- Pointer dogrulama: 5/5 PASS (BP + IA_Throttle/Brake/Steer + IMC_AF_Drive,
  `git show HEAD:<path>` ile git-lfs pointer icerigi dogrulandi).
- Calisma agaci temiz (uasset kalinti yok; OPEN-076-A PNG'lerine dokunulmadi).

### Yan ders (surec)
- Ilk commit denemesi bos gecti: disk klasoru `vehicle/` (kucuk) vs repo yolu
  `Vehicle/` (buyuk). `git add` disk-casing yolla eslesmedi; `git show HEAD:`
  kucuk harfli yolda 5 sahte POINTER FAIL uretti. Cozum: pathler repo-casing
  ile sabit verildi. Kural: pointer/tree kontrollerinde daima `git ls-files`
  casing'i kullanilir (git indeksi harfe duyarli, Windows FS degil).

### Sonraki adim
- M5.4e: `m54e_make_map.py` - GameMode (DefaultPawn=BP_AF_VehiclePawn) +
  Map_AF_DriveTest (duz zemin + PlayerStart + GameMode override) UE Python ile.

---

## D-097 - M5.4e KAPANDI: GameMode + test haritasi (7/7 PASS)

**Tarih:** 2026-08-15
**Durum:** KAPALI
**Ilgili:** D-092 (M5.4 plani, M5.4e satiri), D-096 (casing kurali), D-095 (DataAssetFactory)

### Yontem
`BlenderPipeline/tools/m54e_make_map.py` (commit 2f1b963) UE Python ile kosuldu;
tamamen script, GUI adimi yok (SCRIPT-FIRST tam uyum).

### Sonuclar (kanit: LogPython, 7/7 PASS)
- GM-CLASS : BP_AF_GameMode (GameModeBase turevi BP) uretildi.
- GM-PAWN  : default_pawn_class = BP_AF_VehiclePawn_C (readback dogrulamali).
- LEVEL    : /Game/vehicle/Map_AF_DriveTest yaratildi ve yuklendi.
- FLOOR    : StaticMeshActor zemin, scale=(100,100,1), loc=(0,0,-50).
- PSTART   : PlayerStart loc=(0,0,150).
- GMODE-OVR: WorldSettings.default_game_mode = BP_AF_GameMode_C.
- SAVE     : map_exists=True; MapCheck: 0 Error, 0 Warning.
- SONUC    : PASS - "M5.4e tamam; M5.4f surus kabulune gec".

### Yan kayit
- "Unable to Check Out From Revision Control" dialogu zararsiz: UE'de revision
  control saglayicisi bagli degil; SavePackage yine de diske yazdi (SAVE PASS).

### LFS commit
- `01b30b6` : Unreal/Content/Vehicle/BP_AF_GameMode.uasset +
  Map_AF_DriveTest.umap (repo-casing `Vehicle/`, D-096 kurali uygulanmis).
- Pointer dogrulama index uzerinden (`git show :<path>`): 2/2 PASS.
- LFS upload 2/2 (34 KB); calisma agaci temiz.

### Sonraki adim
- M5.4f: `m54f_drive_test.py` - PIE surus kabul testi (D-092 kriterleri:
  Z stabilite +-50cm/5s, W ile >=10m/5s, A/D yaw, S durus; pozisyon-log
  OTOMATIK KONTROL + tek screenshot, PNG repoya girmez).
- M5.4f PASS sonrasi: M5.4/M5/M2 kapanisi + MILESTONE_PLAN.md tek gecis.

---

## D-098 - M5.5 kok neden analizi (AYRI SAYFA)

**Tarih:** 2026-08-17
**Durum:** ACIK (m56s v4 PASS; m56m_drive_test_v2 UE kosumu bekliyor)

Tam kayit: `DECISION_LOG_VOL17_D098.md` (bu ciltte sayfa buyudugu icin ayri dosya).
Ozet: torque OK / XY=0 blokajinin root-bone hipotezi ARASTIRMACI kanitiyla
ELENDI (`CanCreateVehicle()` root-bone sarti icermiyor); `bone_name` Python'dan
read-only oldugu icin m56r rebind yolu GECERSIZ; birincil hipotez oversized
chassis collision box. Cozum scriptleri repoda:
`BlenderPipeline/tools/m56s_shrink_chassis.py` (box shrink, QA-hardened) +
`m56m_drive_test_v2.py` (settle-aware PIE kabul testi). Kabul: m56s != FAIL
VE m56m SONUC: PASS. Not: m55e..m56r chat-only teshis scriptleri bilerek repoya
alinmadi; yalnizca nihai iki script push edildi.

Duzeltme (2026-08-17): m56s v4 UE kosumu PASS - sasi collision box olculdu ve
duzeltildi (actor-space taban -46.7 cm -> +2.4 cm), PhysicsAsset kaydedildi
(.uasset LFS commit'i bekliyor). XY=0 icin nedensellik ve surus kabulu
m56m_drive_test_v2 kosumuna kadar dogrulanmamis sayilir; kosum bloke
(gelistirme makinesi erisilemez). Bu paragraf eski ozetin acik durum
duzeltmesidir; kayit yeniden yazilmamistir.
