# m54c_make_pawn.py - M5.4c: BP_AF_VehiclePawn olustur (D-092)
# WheeledVehiclePawn turevi BP; mesh=AF_Vehicle_Proto, 4 WheelSetup, mass=800,
# duz tork egrisi. Idempotent: asset varsa yeniden yaratmaz, property'leri yazar.
# ASCII only. Cikti: ===== OTOMATIK KONTROL ===== + PASS/FAIL satirlari.
import unreal

PAWN_PATH = "/Game/vehicle/BP_AF_VehiclePawn"
MESH_PATH = "/Game/vehicle/AF_Vehicle_Proto"
WHEEL_F = "/Game/vehicle/BP_AF_Wheel_Front"
WHEEL_R = "/Game/vehicle/BP_AF_Wheel_Rear"
WHEEL_MAP = [
    (WHEEL_F, "AF_Wheel_FL"),
    (WHEEL_F, "AF_Wheel_FR"),
    (WHEEL_R, "AF_Wheel_RL"),
    (WHEEL_R, "AF_Wheel_RR"),
]
MASS_KG = 800.0

results = []
def check(tag, ok, msg):
    results.append(ok)
    print("%-6s: %s - %s" % (tag, "PASS" if ok else "FAIL", msg))

print("===== OTOMATIK KONTROL =====")

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()

# 1) BP asset (idempotent)
if not eal.does_asset_exist(PAWN_PATH):
    parent = unreal.load_class(None, "/Script/ChaosVehicles.WheeledVehiclePawn")
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    at.create_asset("BP_AF_VehiclePawn", "/Game/vehicle", None, factory)
bp = unreal.load_asset(PAWN_PATH)
check("BP", bp is not None, "BP_AF_VehiclePawn hazir")

gen_cls = unreal.load_object(None, PAWN_PATH + ".BP_AF_VehiclePawn_C")
cdo = unreal.get_default_object(gen_cls) if gen_cls else None
check("CDO", cdo is not None, "generated class CDO alindi")

# 2) Mesh component: skeletal mesh ata
mesh_ok = False
mesh_comp = None
if cdo:
    for prop in ("mesh",):
        try:
            mesh_comp = cdo.get_editor_property(prop)
            break
        except Exception:
            pass
sk = unreal.load_asset(MESH_PATH)
if mesh_comp and sk:
    for prop in ("skeletal_mesh_asset", "skeletal_mesh"):
        try:
            mesh_comp.set_editor_property(prop, sk)
            rb = mesh_comp.get_editor_property(prop)
            mesh_ok = rb is not None and rb.get_path_name().startswith(MESH_PATH)
            if mesh_ok:
                break
        except Exception:
            pass
check("MESH", mesh_ok, "AF_Vehicle_Proto mesh'e atandi (read-back)")

# 3) Movement component: wheel setups + mass + tork
move = None
if cdo:
    for prop in ("vehicle_movement_component", "vehicle_movement"):
        try:
            move = cdo.get_editor_property(prop)
            break
        except Exception:
            pass
check("MOVE", move is not None, "ChaosWheeledVehicleMovementComponent alindi")

wheels_ok = False
if move:
    try:
        setups = []
        for cls_path, bone in WHEEL_MAP:
            wcls = unreal.load_object(None, cls_path + "." + cls_path.split("/")[-1] + "_C")
            s = unreal.ChaosWheelSetup()
            s.set_editor_property("wheel_class", wcls)
            s.set_editor_property("bone_name", bone)
            setups.append(s)
        move.set_editor_property("wheel_setups", setups)
        rb = move.get_editor_property("wheel_setups")
        bones = [str(x.get_editor_property("bone_name")) for x in rb]
        wheels_ok = bones == [b for _, b in WHEEL_MAP] and all(
            x.get_editor_property("wheel_class") is not None for x in rb)
        detail = ",".join(bones)
    except Exception as e:
        detail = "hata: %s" % e
    check("WHEEL", wheels_ok, "4 wheel setup: %s" % detail)
else:
    check("WHEEL", False, "movement component yok")

mass_ok = False
if move:
    try:
        move.set_editor_property("mass", MASS_KG)
        mass_ok = abs(move.get_editor_property("mass") - MASS_KG) < 0.5
    except Exception:
        pass
check("MASS", mass_ok, "mass = 800 kg")

# 4) Tork egrisi: duz 300 Nm (0..5000 rpm), 6000'de 0.
tork_ok = False
tork_msg = ""
if move:
    try:
        eng = move.get_editor_property("engine_setup")
        curve = eng.get_editor_property("torque_curve")
        rich = curve.get_editor_property("editor_curve_data")
        keys = []
        for t, v in ((0.0, 300.0), (5000.0, 300.0), (6000.0, 0.0)):
            k = unreal.RichCurveKey()
            k.set_editor_property("time", t)
            k.set_editor_property("value", v)
            keys.append(k)
        rich.set_editor_property("keys", keys)
        curve.set_editor_property("editor_curve_data", rich)
        eng.set_editor_property("torque_curve", curve)
        move.set_editor_property("engine_setup", eng)
        rb = move.get_editor_property("engine_setup").get_editor_property(
            "torque_curve").get_editor_property("editor_curve_data")
        n = len(rb.get_editor_property("keys"))
        tork_ok = n == 3
        tork_msg = "in-place rich curve, %d key" % n
    except Exception as e:
        tork_msg = "in-place FAIL (%s), external curve denenecek" % e
    if not tork_ok:
        try:
            CURVE_PATH = "/Game/vehicle/Curve_AF_Torque"
            if not eal.does_asset_exist(CURVE_PATH):
                cf = unreal.CurveFloatFactory()
                at.create_asset("Curve_AF_Torque", "/Game/vehicle", None, cf)
            cassets = unreal.load_asset(CURVE_PATH)
            fc = cassets.get_editor_property("float_curve")
            keys = []
            for t, v in ((0.0, 300.0), (5000.0, 300.0), (6000.0, 0.0)):
                k = unreal.RichCurveKey()
                k.set_editor_property("time", t)
                k.set_editor_property("value", v)
                keys.append(k)
            fc.set_editor_property("keys", keys)
            cassets.set_editor_property("float_curve", fc)
            eal.save_asset(CURVE_PATH)
            eng = move.get_editor_property("engine_setup")
            curve = eng.get_editor_property("torque_curve")
            curve.set_editor_property("external_curve", cassets)
            eng.set_editor_property("torque_curve", curve)
            move.set_editor_property("engine_setup", eng)
            tork_ok = True
            tork_msg = "external CurveFloat baglandi (Curve_AF_Torque)"
        except Exception as e:
            tork_msg += " | external FAIL: %s" % e
check("TORK", tork_ok, tork_msg)

# 5) Compile + save
try:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
except Exception as e:
    print("uyari: compile atlandi (%s)" % e)
saved = eal.save_asset(PAWN_PATH)
check("SAVE", bool(saved), "BP_AF_VehiclePawn kaydedildi")

if all(results):
    print("SONUC : PASS - M5.4c tamam; M5.4d (Enhanced Input) adimina gec")
else:
    print("SONUC : FAIL - ciktiyi yapistir; 2. FAIL'de hibrit modele gecilir (D-087)")
