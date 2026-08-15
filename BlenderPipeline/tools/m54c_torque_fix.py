# m54c_torque_fix.py - M5.4c v3: torque curve via CSV-imported CurveFloat + external_curve
# Neden: UE 5.8.1 Python'da RuntimeFloatCurve.editor_curve_data ve CurveFloat.float_curve
# expose degil (v2 TORK FAIL kaniti). Yontem degisikligi (D-087): CSVImportFactory ile
# CurveFloat asset'i yarat, RuntimeFloatCurve.external_curve'e bagla, zinciri geri yaz.
import os
import tempfile
import unreal

BP_PATH = "/Game/vehicle/BP_AF_VehiclePawn"
CURVE_DIR = "/Game/vehicle"
CURVE_NAME = "Curve_AF_Torque"
CURVE_PATH = CURVE_DIR + "/" + CURVE_NAME
KEYS = [(0.0, 300.0), (5000.0, 300.0), (6000.0, 0.0)]

failed = []

def log(tag, ok, msg):
    s = "PASS" if ok else "FAIL"
    if not ok:
        failed.append(tag)
    unreal.log("%-6s: %s - %s" % (tag, s, msg))

unreal.log("===== OTOMATIK KONTROL =====")

# --- 1. BP + CDO + movement ---
cdo = None
move = None
try:
    bp = unreal.load_asset(BP_PATH)
    gen_cls = unreal.load_object(None, BP_PATH + "." + "BP_AF_VehiclePawn_C")
    cdo = unreal.get_default_object(gen_cls)
    log("CDO", cdo is not None, "default object alindi")
except Exception as e:
    log("CDO", False, repr(e))

if cdo is not None:
    for prop in ("vehicle_movement_component", "vehicle_movement"):
        try:
            move = cdo.get_editor_property(prop)
            if move is not None:
                log("MOVE", True, "prop=" + prop)
                break
        except Exception:
            move = None
    if move is None:
        log("MOVE", False, "movement component bulunamadi")

# --- 2. Envanter (tani icin her kosulda bas) ---
try:
    eng = move.get_editor_property("engine_setup")
    tc = eng.get_editor_property("torque_curve")
    props = [p for p in dir(tc) if not p.startswith("_") and p not in (
        "cast", "copy", "static_struct", "to_tuple", "assign", "call_method",
        "export_text", "import_text", "get_editor_property", "set_editor_property",
        "set_editor_properties")]
    unreal.log("ENVANTER RuntimeFloatCurve uyeleri: " + ",".join(props))
except Exception as e:
    unreal.log("ENVANTER FAIL: " + repr(e))

# --- 3. CSV ile CurveFloat yarat (varsa yeniden import etmez, direkt yukler) ---
curve = None
try:
    curve = unreal.load_asset(CURVE_PATH)
except Exception:
    curve = None

if curve is None:
    try:
        csv_path = os.path.join(tempfile.gettempdir(), "af_torque.csv")
        with open(csv_path, "w") as f:
            for t, v in KEYS:
                f.write("%s,%s\n" % (t, v))
        factory = unreal.CSVImportFactory()
        try:
            s = unreal.CSVImportSettings()
            s.import_type = unreal.CSVImportType.ECSV_CURVE_FLOAT
            factory.set_editor_property("automated_import_settings", s)
        except Exception as e2:
            unreal.log("CSV ayar uyarisi: " + repr(e2))
        task = unreal.AssetImportTask()
        task.filename = csv_path
        task.destination_path = CURVE_DIR
        task.destination_name = CURVE_NAME
        task.automated = True
        task.replace_existing = True
        task.save = True
        task.factory = factory
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        curve = unreal.load_asset(CURVE_PATH)
    except Exception as e:
        log("CSV", False, repr(e))

if curve is not None:
    try:
        v0 = curve.get_float_value(0.0)
        v5k = curve.get_float_value(5000.0)
        v6k = curve.get_float_value(6000.0)
        ok = abs(v0 - 300.0) < 1.0 and abs(v5k - 300.0) < 1.0 and abs(v6k) < 1.0
        log("CURVE", ok, "v(0)=%.1f v(5000)=%.1f v(6000)=%.1f (hedef 300/300/0)" % (v0, v5k, v6k))
    except Exception as e:
        log("CURVE", False, "deger okunamadi: " + repr(e))
else:
    log("CURVE", False, "CurveFloat asset yaratilmadi/yuklenemedi")

# --- 4. external_curve bagla + zinciri geri yaz ---
if move is not None and curve is not None:
    bound = False
    try:
        eng = move.get_editor_property("engine_setup")
        tc = eng.get_editor_property("torque_curve")
        for prop in ("external_curve", "curve"):
            try:
                tc.set_editor_property(prop, curve)
                bound = True
                used = prop
                break
            except Exception as e1:
                last = repr(e1)
        if bound:
            eng.set_editor_property("torque_curve", tc)
            move.set_editor_property("engine_setup", eng)
            # read-back
            eng2 = move.get_editor_property("engine_setup")
            tc2 = eng2.get_editor_property("torque_curve")
            c2 = tc2.get_editor_property(used)
            ok = c2 is not None and c2.get_name() == CURVE_NAME
            log("TORK", ok, "prop=%s readback=%s" % (used, c2.get_name() if c2 else "None"))
        else:
            log("TORK", False, "hicbir property tutmadi, son hata: " + last)
    except Exception as e:
        log("TORK", False, repr(e))
else:
    log("TORK", False, "on kosullar eksik (MOVE/CURVE)")

# --- 5. compile + save ---
try:
    bp = unreal.load_asset(BP_PATH)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        log("COMP", True, "compile_blueprint calisti")
    except Exception as e:
        unreal.log("COMP uyari: " + repr(e))
    s1 = unreal.EditorAssetLibrary.save_asset(BP_PATH)
    s2 = unreal.EditorAssetLibrary.save_asset(CURVE_PATH) if curve is not None else False
    log("SAVE", s1, "pawn=%s curve=%s" % (s1, s2))
except Exception as e:
    log("SAVE", False, repr(e))

if failed:
    unreal.log("SONUC : FAIL - dusen adimlar: %s; TAM ciktiyi yapistir (FAIL = D-087 hibrit GUI)" % ",".join(failed))
else:
    unreal.log("SONUC : PASS - M5.4c TAMAM: tork egrisi external CurveFloat ile bagli; uasset commit adimina gec")
