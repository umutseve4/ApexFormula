# m54c_fix_pawn.py - M5.4c v2 (D-092): BP_AF_VehiclePawn repair + verbose diagnostics
# Rule: UE Python get_editor_property returns COPIES for structs/arrays.
#       Every edit must be written back up the chain (copy -> modify -> set-back).
# ASCII-only output. Prints "===== OTOMATIK KONTROL =====" block with PASS/FAIL per step.

import unreal

ASSET_DIR = "/Game/vehicle"
PAWN_NAME = "BP_AF_VehiclePawn"
PAWN_PATH = ASSET_DIR + "/" + PAWN_NAME
MESH_PATH = ASSET_DIR + "/AF_Vehicle_Proto"
CURVE_PATH = ASSET_DIR + "/Curve_AF_Torque"
MASS_TARGET = 800.0
TORQUE_KEYS = [(0.0, 300.0), (5000.0, 300.0), (6000.0, 0.0)]
WHEELS = [
    ("BP_AF_Wheel_Front", "AF_Wheel_FL"),
    ("BP_AF_Wheel_Front", "AF_Wheel_FR"),
    ("BP_AF_Wheel_Rear",  "AF_Wheel_RL"),
    ("BP_AF_Wheel_Rear",  "AF_Wheel_RR"),
]

fails = []

def log(tag, ok, detail):
    state = "PASS" if ok else "FAIL"
    if not ok:
        fails.append(tag)
    unreal.log("%s : %s - %s" % (tag, state, detail))

unreal.log("===== OTOMATIK KONTROL =====")

# ---- 1. load blueprint + generated class + CDO ----
bp = unreal.load_asset(PAWN_PATH)
cls = unreal.load_object(None, PAWN_PATH + "." + PAWN_NAME + "_C")
cdo = None
if cls:
    try:
        cdo = unreal.get_default_object(cls)
    except Exception as e:
        unreal.log("CDO exception: %r" % (e,))
log("BP", bp is not None, "asset %s" % ("yuklendi" if bp else "YOK"))
log("CDO", cdo is not None, "default object %s" % ("alindi" if cdo else "YOK"))

if cdo is None:
    unreal.log("SONUC : FAIL - CDO alinamadi; ciktiyi yapistir (D-087 hibrit adayi)")
    raise SystemExit(0)

# ---- 2. mesh component + skeletal mesh ----
mesh_comp = None
mesh_err = ""
for prop in ("mesh",):
    try:
        mesh_comp = cdo.get_editor_property(prop)
        break
    except Exception as e:
        mesh_err = repr(e)
sm = unreal.load_asset(MESH_PATH)
mesh_ok = False
mesh_detail = ""
if mesh_comp and sm:
    set_ok = False
    for prop in ("skeletal_mesh_asset", "skeletal_mesh"):
        try:
            mesh_comp.set_editor_property(prop, sm)
            set_ok = True
            mesh_detail = "prop=" + prop
            break
        except Exception as e:
            mesh_detail = repr(e)
    if not set_ok:
        try:
            mesh_comp.set_skeletal_mesh_asset(sm)
            set_ok = True
            mesh_detail = "method=set_skeletal_mesh_asset"
        except Exception as e:
            mesh_detail = mesh_detail + " | " + repr(e)
    if set_ok:
        try:
            got = mesh_comp.get_skeletal_mesh_asset()
        except Exception:
            got = None
        mesh_ok = (got is not None and got.get_name() == "AF_Vehicle_Proto")
        mesh_detail = mesh_detail + " readback=" + (got.get_name() if got else "None")
else:
    mesh_detail = "mesh_comp=%s sm=%s err=%s" % (bool(mesh_comp), bool(sm), mesh_err)
log("MESH", mesh_ok, mesh_detail)

# ---- 3. movement component ----
move = None
move_err = []
for prop in ("vehicle_movement_component", "vehicle_movement"):
    try:
        move = cdo.get_editor_property(prop)
        if move:
            move_detail = "prop=" + prop
            break
    except Exception as e:
        move_err.append(repr(e))
if move is None:
    move_detail = " | ".join(move_err) if move_err else "bulunamadi"
log("MOVE", move is not None, move_detail)

wheel_ok = False
mass_ok = False
tork_ok = False
if move:
    # ---- 4. wheel setups (array copy -> build fresh -> set back) ----
    try:
        arr = []
        for bp_name, bone in WHEELS:
            wcls = unreal.load_object(None, ASSET_DIR + "/" + bp_name + "." + bp_name + "_C")
            s = unreal.ChaosWheelSetup()
            s.set_editor_property("wheel_class", wcls)
            s.set_editor_property("bone_name", bone)
            arr.append(s)
        move.set_editor_property("wheel_setups", arr)
        back = move.get_editor_property("wheel_setups")
        bones = [str(x.get_editor_property("bone_name")) for x in back]
        wheel_ok = (len(back) == 4 and bones == [w[1] for w in WHEELS])
        log("WHEEL", wheel_ok, "n=%d bones=%s" % (len(back), ",".join(bones)))
    except Exception as e:
        log("WHEEL", False, repr(e))

    # ---- 5. mass ----
    try:
        move.set_editor_property("mass", MASS_TARGET)
        m = float(move.get_editor_property("mass"))
        mass_ok = abs(m - MASS_TARGET) < 0.5
        log("MASS", mass_ok, "mass=%.1f (hedef %.1f)" % (m, MASS_TARGET))
    except Exception as e:
        log("MASS", False, repr(e))

    # ---- 6. torque curve: copy -> modify -> SET BACK whole chain ----
    tork_detail = ""
    try:
        eng = move.get_editor_property("engine_setup")          # copy
        tc = eng.get_editor_property("torque_curve")            # copy (RuntimeFloatCurve)
        done = False
        # 6a. in-place rich curve keys
        try:
            rc = tc.get_editor_property("editor_curve_data")    # copy (RichCurve)
            keys = []
            for t, v in TORQUE_KEYS:
                k = unreal.RichCurveKey()
                k.set_editor_property("time", t)
                k.set_editor_property("value", v)
                keys.append(k)
            rc.set_editor_property("keys", keys)
            tc.set_editor_property("editor_curve_data", rc)     # set back level 1
            done = True
            tork_detail = "yol=editor_curve_data"
        except Exception as e1:
            tork_detail = "inplace: " + repr(e1)
        # 6b. fallback: external CurveFloat asset
        if not done:
            curve = unreal.load_asset(CURVE_PATH)
            if curve is None:
                at = unreal.AssetToolsHelpers.get_asset_tools()
                curve = at.create_asset("Curve_AF_Torque", ASSET_DIR,
                                        unreal.CurveFloat, unreal.CurveFloatFactory())
            keys = []
            for t, v in TORQUE_KEYS:
                k = unreal.RichCurveKey()
                k.set_editor_property("time", t)
                k.set_editor_property("value", v)
                keys.append(k)
            rc2 = unreal.RichCurve()
            rc2.set_editor_property("keys", keys)
            curve.set_editor_property("float_curve", rc2)
            unreal.EditorAssetLibrary.save_asset(CURVE_PATH)
            tc.set_editor_property("external_curve", curve)
            done = True
            tork_detail = tork_detail + " | yol=external_curve"
        eng.set_editor_property("torque_curve", tc)             # set back level 2
        move.set_editor_property("engine_setup", eng)           # set back level 3
        # read back
        eng2 = move.get_editor_property("engine_setup")
        tc2 = eng2.get_editor_property("torque_curve")
        n_keys = 0
        try:
            n_keys = len(tc2.get_editor_property("editor_curve_data").get_editor_property("keys"))
        except Exception:
            pass
        ext = None
        try:
            ext = tc2.get_editor_property("external_curve")
        except Exception:
            pass
        tork_ok = (n_keys >= 3) or (ext is not None)
        log("TORK", tork_ok, "%s readback keys=%d ext=%s" % (tork_detail, n_keys, ext.get_name() if ext else "None"))
    except Exception as e:
        log("TORK", False, tork_detail + " | " + repr(e))

# ---- 7. compile + save ----
try:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    log("COMP", True, "compile_blueprint calisti")
except Exception as e:
    log("COMP", False, repr(e))
try:
    saved = unreal.EditorAssetLibrary.save_asset(PAWN_PATH)
    log("SAVE", bool(saved), PAWN_NAME + (" kaydedildi" if saved else " KAYDEDILEMEDI"))
except Exception as e:
    log("SAVE", False, repr(e))

if fails:
    unreal.log("SONUC : FAIL - dusen adimlar: %s; TAM ciktiyi yapistir (2. FAIL = D-087 hibrit)" % ",".join(fails))
else:
    unreal.log("SONUC : PASS - M5.4c tamam; pawn uasset'ini commit et, M5.4d'ye (Enhanced Input) gec")
