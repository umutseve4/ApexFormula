# D-098 - M5.5 kok neden analizi: root-bone hipotezi ELENDI, collision-shrink birincil yol

(Bu dosya DECISION_LOG_VOL17.md'ye eklenmek uzere ayri tutuldu; VOL17 buyudugu
icin ayri sayfa. Sonraki ciltte birlestirilebilir.)

**Tarih:** 2026-08-17
**Durum:** ACIK (m56s + m56m_v2 UE kosumu bekliyor)
**Ilgili:** D-097 (M5.4e), m56a..m56r chat-only teshis zinciri

## Baglam: chat-only script acigi
m55e..m56r arasi ~15 teshis scripti yalnizca sohbet icinde uretildi, repoya
girmedi (surec ihlali; bu kayitla kapatiliyor). Kilit bulgular:
- m56f: tam gazda arka tekerlek acisal hiz 1978.9 -> drivetrain SAGLIKLI.
- m56q: govde yerden ~99 cm yukarida asili kaliyor (fizik canli, XY=0).
- m55x/m56 serisi: torque uygulaniyor ama XY yer degistirme 0.0 cm.

## Arastirma bulgulari (ARASTIRMACI ajani, UE kaynak kodu kanitli)
1. **Root-bone hipotezi ELENDI:** Chaos `CanCreateVehicle()` icinde root-bone
   body sarti YOK. PA body'sinin root bone'a bagli olmamasi sorun degil.
2. **`BodySetup.bone_name` Python'dan READ-ONLY** -> m56r rebind scripti
   GECERSIZ (superseded, repoya alinmadi).
3. **`agg_geom` Read-Write:** `copy() -> eleman degistir -> box_elems set ->
   agg_geom set -> save_loaded_asset` kalibi calisiyor. In-place mutasyon YASAK.

## Yeni birincil hipotez
Chassis collision box asiri buyuk -> govde box'i tekerleklerden ONCE zemine
deger -> suspansiyon raycast'leri zemine ulasamaz -> tekerlekler bosta doner
(m56f kaniti) -> XY hareket 0. Fix: box alt yuzeyini tekerlek merkezinin
2 cm ustune cek (ust yuzey sabit).

## Teslim edilen scriptler (QA'den gecti - DENETIM ajani, PARTIAL->duzeltmeler uygulandi)
- `BlenderPipeline/tools/m56s_shrink_chassis.py`: chassis'i bone_name ile
  POZITIF secer (ilk-box'li sezgisi YASAK), rotasyonlu box/bone'da IPTAL eder
  (PhAT GUI fallback), bone scale'i hesaba katar, try/finally temizlik,
  ScopedEditorTransaction + save + persist readback. SONUC: PASS/FAIL/BILGI
  (BILGI = box zaten dogru -> hipotez yanlis -> m56m ile dogrula).
- `BlenderPipeline/tools/m56m_drive_test_v2.py`: PIE'yi kendisi baslatir
  (slate post-tick), PIE world'u `UnrealEditorSubsystem.get_game_world()` ile
  alir, m56q unfreeze dahili, settle t=3s, olcum t=12s.
  Kabul: XY>300cm VE speed>100cm/s (zdrop>20 bilgilendirici).

## QA kabul edilen riskler
- Runtime unfreeze asset-seviyesi fix'i maskeleyebilir -> kabul: bu bir smoke
  test; kalici cozum dogrulanirsa unfreeze'siz tekrar kosulacak.
- Kayit sonrasi canli BodyInstance guncellenmez -> m56m taze PIE baslattigi
  icin sorun degil.

## Kabul kriteri (M5.5 kapanisi)
m56s SONUC != FAIL VE m56m SONUC: PASS. PASS sonrasi: uasset LFS commit
(UE KAPALI iken), MILESTONE_PLAN M5.5 kapanisi, D-098 KAPALI.
