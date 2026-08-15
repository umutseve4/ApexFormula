# m54c_curve_fix_v4.py - D-092 M5.4c v4 (D-087: v3 ilk FAIL -> tek duzeltilmis deneme)
# Sorun: v3 CSV import key'siz CurveFloat uretti (v(0)=v(5000)=v(6000)=0.0).
# Duzeltmeler:
#   1) CSVImportFactory.automated_import_settings acikca ECSV_CURVE_FLOAT yapilir
#      (copy -> modify -> set-back; exception YUTULMAZ, verbose yazilir)
#   2) CSV basliksiz: her satir "zaman,deger"
#   3) AssetImportTask.replace_existing=True -> ayni asset ustune reimport
#   4) Import sonrasi get_float_value ile sayisal dogrulama + rebind + save
import unreal
import os
import tempfile

PAWN_PATH = "/Game/vehicle/BP_AF_VehiclePawn"
CURVE_DIR = "/Game/vehicle"
CURVE_NAME = "Curve_AF_Torque"
CURVE_PATH = CURVE_DIR + "/" + CURVE_NAME
KEYS = [(0.0, 300.0), (5000.0, 300.0), (6000.0, 0.0)]
TOL = 1.0

steps = {}

def log(msg):
    unreal.log(msg)

log("===== OTOMATIK KONTROL =====")

# --- 1) CSV dosyasi (BASLIKSIZ) ---
csv_path = os.path.join(tempfile.gettempdir(), "af_torque_v4.csv")
try:
    with open(csv_path, "w") as f:
        for t, v in KEYS:
            f.write("%g,%g\n" % (t, v))
    with open(csv_path, "r") as f:
        content = f.read().replace("\n", " | ")
    steps["CSVFILE"] = True
    log("CSVFILE : PASS - %s icerik: %s" % (csv_path, content))
except Exception as e:
    steps["CSVFILE"] = False
    log("CSVFILE : FAIL - %r" % e)

# --- 2) Factory ayarlari (copy -> modify -> set-back, yutma yok) ---
factory = None
try:
    factory = unreal.CSVImportFactory()
    s = factory.automated_import_settings
    log("AYAR-ONCE : import_type=%s" % s.import_type)
    s.import_type = unreal.CSVImportType.ECSV_CURVE_FLOAT
    try:
        s.import_curve_interp_mode = unreal.RichCurveInterpMode.RCIM_LINEAR
        log("AYAR : interp=RCIM_LINEAR set edildi")
    except Exception as e2:
        log("AYAR : interp set edilemedi (kritik degil): %r" % e2)
    factory.automated_import_settings = s
    s2 = factory.automated_import_settings
    ok = (s2.import_type == unreal.CSVImportType.ECSV_CURVE_FLOAT)
    steps["AYAR"] = ok
    log("AYAR : %s - readback import_type=%s" % ("PASS" if ok else "FAIL", s2.import_type))
except Exception as e:
    steps["AYAR"] = False
    log("AYAR : FAIL - %r" % e)

# --- 3) Reimport (replace_existing) ---
curve = None
try:
    task = unreal.AssetImportTask()
    task.filename = csv_path
    task.destination_path = CURVE_DIR
    task.destination_name = CURVE_NAME
    task.replace_existing = True
    task.automated = True
    task.save = False
    task.factory = factory
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = list(task.imported_object_paths) if task.imported_object_paths else []
    log("IMPORT : imported_object_paths=%s" % imported)
    curve = unreal.load_asset(CURVE_PATH)
    steps["IMPORT"] = curve is not None
    log("IMPORT : %s - curve=%s sinif=%s" % (
        "PASS" if curve else "FAIL",
        curve.get_name() if curve else "None",
        type(curve).__name__ if curve else "-"))
except Exception as e:
    steps["IMPORT"] = False
    log("IMPORT : FAIL - %r" % e)

# --- 4) Sayisal dogrulama ---
try:
    vals = [curve.get_float_value(t) for t, _ in KEYS]
    ok = all(abs(vals[i] - KEYS[i][1]) <= TOL for i in range(len(KEYS)))
    try:
        tmin, tmax = curve.get_time_range()
        vmin, vmax = curve.get_value_range()
        log("ARALIK : zaman=[%g,%g] deger=[%g,%g]" % (tmin, tmax, vmin, vmax))
    except Exception as e3:
        log("ARALIK : okunamadi: %r" % e3)
    steps["CURVE"] = ok
    log("CURVE : %s - v(0)=%g v(5000)=%g v(6000)=%g (hedef 300/300/0)" % (
        "PASS" if ok else "FAIL", vals[0], vals[1], vals[2]))
except Exception as e:
    steps["CURVE"] = False
    log("CURVE : FAIL - %r" % e)

# --- 5) Rebind (reimport yeni obje yaratmis olabilir) ---
pawn_bp = None
try:
    pawn_bp = unreal.load_asset(PAWN_PATH)
    gen_class = pawn_bp.generated_class()
    cdo = unreal.get_default_object(gen_class)
    move = cdo.get_editor_property("vehicle_movement_component")
    eng = move.get_editor_property("engine_setup")
    tc = eng.get_editor_property("torque_curve")
    tc.set_editor_property("external_curve", curve)
    eng.set_editor_property("torque_curve", tc)
    move.set_editor_property("engine_setup", eng)
    rb = (move.get_editor_property("engine_setup")
              .get_editor_property("torque_curve")
              .get_editor_property("external_curve"))
    ok = rb is not None and rb.get_name() == CURVE_NAME
    steps["TORK"] = ok
    log("TORK : %s - readback=%s" % ("PASS" if ok else "FAIL", rb.get_name() if rb else "None"))
except Exception as e:
    steps["TORK"] = False
    log("TORK : FAIL - %r" % e)

# --- 6) Compile + Save ---
try:
    unreal.BlueprintEditorLibrary.compile_blueprint(pawn_bp)
    steps["COMP"] = True
    log("COMP : PASS - compile_blueprint calisti")
except Exception as e:
    steps["COMP"] = False
    log("COMP : FAIL - %r" % e)

try:
    ok1 = unreal.EditorAssetLibrary.save_asset(PAWN_PATH, only_if_is_dirty=False)
    ok2 = unreal.EditorAssetLibrary.save_asset(CURVE_PATH, only_if_is_dirty=False)
    steps["SAVE"] = ok1 and ok2
    log("SAVE : %s - pawn=%s curve=%s" % ("PASS" if (ok1 and ok2) else "FAIL", ok1, ok2))
except Exception as e:
    steps["SAVE"] = False
    log("SAVE : FAIL - %r" % e)

fails = [k for k, v in steps.items() if not v]
if not fails:
    log("SONUC : PASS - M5.4c TAMAM; commit blogu iste, sonra M5.4d (Enhanced Input)")
else:
    log("SONUC : FAIL - dusen adimlar: %s; TAM ciktiyi yapistir (D-087: hibrit GUI'ye gecilir)" % ",".join(fails))
