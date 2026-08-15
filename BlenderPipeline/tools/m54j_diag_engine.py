# m54j_diag_engine.py - M5.4f drivetrain deneme #3 (YONTEM DEGISIKLIGI)
# Amac: motorun rolantide donma nedenini CDO uzerinde bulmak ve onarmak.
#   1) engine_setup: max_torque / max_rpm / torque_curve (external curve ornekleme)
#   2) wheel_setups: her teker sinifinin affected_by_engine / axle_type bayraklari
#   3) differential + transmission konfigurasyonu
#   4) FIX: hicbir teker affected_by_engine degilse /Game teker BP'lerine yaz;
#          torque curve bos + max_torque<=0 ise max_torque=500 yaz.
# Play GEREKMEZ. Cikti: [M54J] OTOMATIK KONTROL.
import unreal

BP_PATH = "/Game/vehicle/BP_AF_VehiclePawn"
R = []

def log(tag, status, detail=""):
    R.append((tag, status, detail))
    unreal.log("[M54J] {} {}  {}".format(tag, status, detail))

def dump(final):
    unreal.log("[M54J] ===== OTOMATIK KONTROL =====")
    for t, s, d in R:
        unreal.log("[M54J] {:<12}: {}  ({})".format(t, s, d))
    unreal.log("[M54J] SONUC {}".format(final))

def get_prop(obj, names):
    for n in names:
        try:
            return obj.get_editor_property(n), n
        except Exception:
            continue
    return None, None

# ---- 1) CDO + VMC ----
cls = unreal.load_object(None, BP_PATH + ".BP_AF_VehiclePawn_C")
if not cls:
    log("LOAD", "FAIL", "sinif yuklenemedi: " + BP_PATH)
    dump("FAIL"); raise SystemExit
cdo = unreal.get_default_object(cls)
vmc, vmc_name = get_prop(cdo, ["vehicle_movement_component", "vehicle_movement"])
if vmc is None:
    log("VMC", "FAIL", "movement component CDO'da bulunamadi")
    dump("FAIL"); raise SystemExit
log("VMC", "PASS", "{} ({})".format(vmc.get_name(), vmc_name))

# ---- 2) engine_setup ----
es, _ = get_prop(vmc, ["engine_setup"])
eng_fix = False
if es is None:
    log("ENGINE", "FAIL", "engine_setup okunamadi")
else:
    mt, _ = get_prop(es, ["max_torque"])
    mr, _ = get_prop(es, ["max_rpm"])
    ir, _ = get_prop(es, ["engine_idle_rpm"])
    log("ENGINE", "INFO", "max_torque={} max_rpm={} idle_rpm={}".format(mt, mr, ir))
    tc, _ = get_prop(es, ["torque_curve"])
    ext = None
    if tc is not None:
        ext, _ = get_prop(tc, ["external_curve"])
    if ext:
        try:
            pts = ["{}rpm->{:.0f}".format(r, ext.get_float_value(float(r)))
                   for r in (0, 1200, 3000, 4500, 6000)]
            log("TORQUECURVE", "PASS", "external=" + ext.get_name() + " " + " ".join(pts))
        except Exception as e:
            log("TORQUECURVE", "WARN", "external var ama ornekleme hatasi: {}".format(e))
    else:
        # editor_curve_data Python'a acik degil (API defteri) -> okuyamayiz.
        log("TORQUECURVE", "KRITIK", "external_curve YOK; gomulu curve okunamiyor (API kisiti)")
        if mt is not None and float(mt) <= 0.0:
            try:
                es.set_editor_property("max_torque", 500.0)
                vmc.set_editor_property("engine_setup", es)
                eng_fix = True
                log("ENGINE-FIX", "PASS", "max_torque 0 -> 500 yazildi")
            except Exception as e:
                log("ENGINE-FIX", "FAIL", str(e))

# ---- 3) transmission + differential ----
ts, _ = get_prop(vmc, ["transmission_setup"])
if ts is not None:
    fg, _ = get_prop(ts, ["forward_gear_ratios"])
    fr, _ = get_prop(ts, ["final_ratio"])
    au, _ = get_prop(ts, ["use_automatic_gears"])
    n = len(fg) if fg is not None else -1
    log("TRANS", "INFO", "ileri_vites={} final_ratio={} otomatik={}".format(n, fr, au))
ds, _ = get_prop(vmc, ["differential_setup"])
if ds is not None:
    dt, _ = get_prop(ds, ["differential_type"])
    log("DIFF", "INFO", "type={}".format(dt))

# ---- 4) wheel_setups + affected_by_engine ----
wheels, _ = get_prop(vmc, ["wheel_setups"])
driven = 0
fixed_bps = []
if not wheels:
    log("WHEELS", "FAIL", "wheel_setups bos")
else:
    infos = []
    for ws in wheels:
        bone, _ = get_prop(ws, ["bone_name"])
        wcls, _ = get_prop(ws, ["wheel_class"])
        if wcls is None:
            infos.append("{}:SINIF-YOK".format(bone)); continue
        wcdo = unreal.get_default_object(wcls)
        abe, _ = get_prop(wcdo, ["affected_by_engine"])
        ast, _ = get_prop(wcdo, ["affected_by_steering"])
        axl, _ = get_prop(wcdo, ["axle_type"])
        infos.append("{}[{}] eng={} steer={} axle={}".format(
            bone, wcls.get_name(), abe, ast, axl))
        if abe:
            driven += 1
    log("WHEELINFO", "INFO", " | ".join(str(i) for i in infos))
    if driven == 0:
        log("DRIVEN", "KRITIK", "HICBIR teker motora bagli degil -> onarim basliyor")
        seen = set()
        for ws in wheels:
            wcls, _ = get_prop(ws, ["wheel_class"])
            if wcls is None:
                continue
            cpath = wcls.get_path_name()
            if not cpath.startswith("/Game/") or cpath in seen:
                continue
            seen.add(cpath)
            try:
                wcdo = unreal.get_default_object(wcls)
                wcdo.set_editor_property("affected_by_engine", True)
                asset_path = cpath.rsplit(".", 1)[0]
                bp = unreal.load_asset(asset_path)
                if bp:
                    try:
                        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
                    except Exception:
                        pass
                    # compile CDO'yu sifirlayabilir -> tekrar yaz
                    wcdo2 = unreal.get_default_object(wcls)
                    if not wcdo2.get_editor_property("affected_by_engine"):
                        wcdo2.set_editor_property("affected_by_engine", True)
                ok = unreal.EditorAssetLibrary.save_asset(asset_path)
                fixed_bps.append("{}={}".format(asset_path.split("/")[-1], ok))
            except Exception as e:
                fixed_bps.append("{}=HATA:{}".format(cpath, e))
        log("WHEEL-FIX", "PASS" if fixed_bps else "FAIL", " ".join(fixed_bps))
    else:
        log("DRIVEN", "PASS", "motora bagli teker sayisi={}".format(driven))

# ---- 5) ana BP'yi kaydet (engine fix olduysa) ----
if eng_fix:
    bp_main = unreal.load_asset(BP_PATH)
    if bp_main:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(bp_main)
        except Exception:
            pass
    ok = unreal.EditorAssetLibrary.save_asset(BP_PATH)
    log("SAVE-MAIN", "PASS" if ok else "FAIL", "saved={}".format(ok))

# ---- 6) dogrulama (yeniden oku) ----
driven2 = 0
wheels2, _ = get_prop(vmc, ["wheel_setups"])
if wheels2:
    for ws in wheels2:
        wcls, _ = get_prop(ws, ["wheel_class"])
        if wcls is None:
            continue
        abe, _ = get_prop(unreal.get_default_object(wcls), ["affected_by_engine"])
        if abe:
            driven2 += 1
log("VERIFY", "PASS" if driven2 > 0 else "FAIL",
    "motora bagli teker={} (>=1 beklenir)".format(driven2))

final = "PASS - simdi m54f_drive_test.py calistir + Play (BIR KEZ)" if driven2 > 0 else \
        "FAIL - WHEELINFO/TORQUECURVE satirlarini raporla"
dump(final)
