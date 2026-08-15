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
