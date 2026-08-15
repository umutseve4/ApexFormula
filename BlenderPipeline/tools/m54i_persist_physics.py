# m54i_persist_physics.py - M5.4f drivetrain onarimi #2 (D-092 / 2-FAIL kurali)
# Kosum #4 kaniti: simulate_physics BeginPlay'de KAPALIYDI (m54f v3 runtime'da acti,
# arac dustu ama RPM rolantide kaldi, hiz=0). ChaosVehicle drivetrain'i BeginPlay'de
# kurulur; fizik o anda kapaliysa motor-teker baglantisi hic olusmaz.
# Bu script kalici onarim + kanit dokumu yapar:
#   1) BP_AF_VehiclePawn CDO'daki mesh'in BodyInstance.simulate_physics = True
#      (copy -> set-back deseni; D-094'te kanitli) + compile + save + reload-verify.
#   2) KANIT: mesh'in physics asset'i var mi? wheel setup bone adlari mesh'te var mi?
# Kosum: UE Output Log -> py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54i_persist_physics.py"

import unreal

BP_PATH = "/Game/vehicle/BP_AF_VehiclePawn"
RESULTS = []

def log(m):
    unreal.log("[M54I] " + m)

def add(name, ok, detail):
    RESULTS.append((name, ok, detail))
    log("%s %s  %s" % (name, "PASS" if ok else "FAIL", detail))

def get_cdo():
    gen_cls = unreal.load_object(None, BP_PATH + "." + BP_PATH.split("/")[-1] + "_C")
    if not gen_cls:
        return None, None
    return gen_cls, unreal.get_default_object(gen_cls)

def get_mesh_comp(cdo):
    for prop in ("mesh",):
        try:
            m = cdo.get_editor_property(prop)
            if m:
                return m
        except Exception as e:
            log("ERR cdo.%s -> %r" % (prop, e))
    return None

def main():
    gen_cls, cdo = get_cdo()
    if not cdo:
        add("LOAD", False, "BP sinifi yuklenemedi: %s" % BP_PATH)
        return finish()
    add("LOAD", True, "CDO=%s" % cdo.get_name())

    mesh = get_mesh_comp(cdo)
    if not mesh:
        add("MESH", False, "CDO'da mesh komponenti bulunamadi")
        return finish()
    add("MESH", True, mesh.get_name())

    # --- 1) simulate_physics'i kalici yaz (BodyInstance copy -> set-back) ---
    try:
        bi = mesh.get_editor_property("body_instance")
        before = bi.get_editor_property("simulate_physics")
        bi.set_editor_property("simulate_physics", True)
        mesh.set_editor_property("body_instance", bi)
        after = mesh.get_editor_property("body_instance").get_editor_property("simulate_physics")
        add("SIMFIZ-SET", bool(after), "once=%s sonra=%s" % (before, after))
    except Exception as e:
        add("SIMFIZ-SET", False, repr(e))

    # --- 2) KANIT: physics asset + wheel bone eslesmesi ---
    pa_name = "YOK"
    try:
        sk = mesh.get_editor_property("skeletal_mesh_asset")
        pa = sk.get_editor_property("physics_asset") if sk else None
        pa_name = pa.get_name() if pa else "YOK"
        add("PHYSASSET", pa is not None, "mesh=%s physasset=%s" % (sk.get_name() if sk else "None", pa_name))
        vmc = None
        try:
            vmc = cdo.get_editor_property("vehicle_movement_component")
        except Exception:
            for p in ("vehicle_movement",):
                try:
                    vmc = cdo.get_editor_property(p)
                except Exception:
                    pass
        if vmc:
            setups = vmc.get_editor_property("wheel_setups")
            names = [str(ws.get_editor_property("bone_name")) for ws in setups]
            add("WHEELS", len(names) == 4, "n=%d bones=%s" % (len(names), ",".join(names)))
        else:
            add("WHEELS", False, "vehicle movement component CDO'da bulunamadi")
    except Exception as e:
        add("KANIT", False, repr(e))

    # --- compile + save + reload verify (m54g recetesi) ---
    try:
        bp = unreal.load_asset(BP_PATH)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        # compile CDO'yu sifirlayabilir -> tekrar yaz
        gen_cls2, cdo2 = get_cdo()
        mesh2 = get_mesh_comp(cdo2)
        bi2 = mesh2.get_editor_property("body_instance")
        if not bi2.get_editor_property("simulate_physics"):
            bi2.set_editor_property("simulate_physics", True)
            mesh2.set_editor_property("body_instance", bi2)
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        saved = unreal.EditorAssetLibrary.save_asset(BP_PATH)
        # reload-verify
        gen_cls3, cdo3 = get_cdo()
        mesh3 = get_mesh_comp(cdo3)
        final = mesh3.get_editor_property("body_instance").get_editor_property("simulate_physics")
        add("SAVE", bool(saved and final), "saved=%s simfizik_kalici=%s" % (saved, final))
    except Exception as e:
        add("SAVE", False, repr(e))
    finish()

def finish():
    log("===== OTOMATIK KONTROL =====")
    all_ok = all(ok for _, ok, _ in RESULTS)
    for n, ok, d in RESULTS:
        log("%-10s : %s  (%s)" % (n, "PASS" if ok else "FAIL", d))
    log("SONUC %s - %s" % ("PASS" if all_ok else "FAIL",
        "simdi m54f_drive_test.py (v4) calistir + Play" if all_ok
        else "ciktiyi oldugu gibi raporla"))

main()
