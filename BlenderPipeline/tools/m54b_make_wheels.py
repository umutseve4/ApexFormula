# m54b_make_wheels.py - D-092 M5.4b
# BP_AF_Wheel_Front (r=36, direksiyon var, tahrik yok) ve
# BP_AF_Wheel_Rear  (r=38, direksiyon yok, tahrik var) uretir.
# Idempotent: asset varsa yeniden yaratmaz, ozellikleri yeniden yazar.
# Kosum: py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54b_make_wheels.py"
import unreal

print("===== OTOMATIK KONTROL =====")

DEST = "/Game/vehicle"
SPECS = [
    ("BP_AF_Wheel_Front", {"radius": 36.0, "steer": True,  "engine": False, "max_steer": 40.0}),
    ("BP_AF_Wheel_Rear",  {"radius": 38.0, "steer": False, "engine": True,  "max_steer": 0.0}),
]

parent = unreal.load_class(None, "/Script/ChaosVehicles.ChaosVehicleWheel")
at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary

fails = 0
if parent is None:
    print("PARENT: FAIL - ChaosVehicleWheel yuklenemedi (plugin?)")
    fails += 1
else:
    for name, s in SPECS:
        path = "%s/%s" % (DEST, name)
        try:
            if eal.does_asset_exist(path):
                bp = eal.load_asset(path)
            else:
                f = unreal.BlueprintFactory()
                f.set_editor_property("parent_class", parent)
                bp = at.create_asset(name, DEST, None, f)
            if bp is None:
                raise RuntimeError("asset yaratilamadi")
            gen_cls = unreal.load_object(None, "%s.%s_C" % (path, name))
            if gen_cls is None:
                raise RuntimeError("generated class bulunamadi")
            cdo = unreal.get_default_object(gen_cls)
            cdo.set_editor_property("wheel_radius", s["radius"])
            cdo.set_editor_property("affected_by_steering", s["steer"])
            cdo.set_editor_property("affected_by_engine", s["engine"])
            cdo.set_editor_property("affected_by_brake", True)
            cdo.set_editor_property("max_steer_angle", s["max_steer"])
            eal.save_asset(path)
            r = float(cdo.get_editor_property("wheel_radius"))
            st = bool(cdo.get_editor_property("affected_by_steering"))
            en = bool(cdo.get_editor_property("affected_by_engine"))
            br = bool(cdo.get_editor_property("affected_by_brake"))
            ok = (abs(r - s["radius"]) < 0.01 and st == s["steer"]
                  and en == s["engine"] and br)
            print("%s : %s - r=%.1f steer=%s engine=%s brake=%s"
                  % (name, "PASS" if ok else "FAIL", r, st, en, br))
            if not ok:
                fails += 1
        except Exception as e:
            print("%s : FAIL - %s" % (name, e))
            fails += 1

if fails == 0:
    print("SONUC : PASS - M5.4b tamam; 2 teker BP hazir, M5.4c'ye (vehicle pawn) gec")
else:
    print("SONUC : FAIL - %d hata; ciktiyi yapistir" % fails)
