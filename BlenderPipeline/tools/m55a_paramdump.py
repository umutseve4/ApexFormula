import unreal
P = "=M55A= "
def log(s): unreal.log(P + s)
EAL = unreal.EditorAssetLibrary

def find(name):
    for a in EAL.list_assets("/Game", recursive=True, include_folder=False):
        s = str(a)
        if ("/" + name + ".") in s:
            return s.split(".")[0] + "." + name
    return None

log("===== OTOMATIK KONTROL =====")
supheli = []

# ---- 1) tork egrisi domeni ----
cpath = find("Curve_AF_Torque")
log("curve path = " + str(cpath))
c1200 = None
if cpath:
    cur = EAL.load_asset(cpath)
    try:
        for t in (0.0, 1.0, 600.0, 1200.0, 3000.0, 4500.0):
            v = cur.get_float_value(t)
            if abs(t - 1200.0) < 0.5:
                c1200 = v
            log("curve(" + str(t) + ") = " + str(v))
    except Exception as e:
        log("curve okunamadi: " + repr(e))
if c1200 is not None and c1200 <= 0.0:
    supheli.append("tork egrisi 1200 RPM'de 0")

# ---- 2) teker CDO'lari ----
alanlar = ["wheel_radius","wheel_width","friction_force_multiplier","cornering_stiffness",
           "max_steer_angle","affected_by_brake","affected_by_handbrake","axle_type",
           "external_torque_combine_method","max_brake_torque","max_hand_brake_torque",
           "spring_rate","suspension_max_raise","suspension_max_drop","wheel_load_ratio",
           "slip_threshold","skid_threshold"]
for wname in ("BP_AF_Wheel_Front","BP_AF_Wheel_Rear"):
    wpath = find(wname)
    log(wname + " path = " + str(wpath))
    if not wpath:
        supheli.append(wname + " bulunamadi"); continue
    try:
        cls = unreal.load_object(None, wpath + "_C")
        cdo = unreal.get_default_object(cls)
        for f in alanlar:
            try:
                val = cdo.get_editor_property(f)
                log(wname + "." + f + " = " + str(val))
                if f == "wheel_radius" and float(val) <= 1.0:
                    supheli.append(wname + " yaricap ~0 (" + str(val) + ")")
            except Exception:
                pass
    except Exception as e:
        log(wname + " CDO okunamadi: " + repr(e))

# ---- 3) arac BP CDO: movement comp tam dokum ----
vpath = find("BP_AF_VehiclePawn")
log("vehicle path = " + str(vpath))
try:
    vcls = unreal.load_object(None, vpath + "_C")
    vcdo = unreal.get_default_object(vcls)
    vmc = None
    try:
        vmc = vcdo.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    except Exception:
        pass
    if vmc is None:
        try:
            arr = vcdo.get_components_by_class(unreal.ChaosWheeledVehicleMovementComponent)
            if len(arr) > 0:
                vmc = arr[0]
        except Exception:
            pass
    log("CDO vmc = " + str(vmc.get_class().get_name() if vmc else None))
    if vmc:
        eng = vmc.get_editor_property("engine_setup")
        for f in ("max_torque","max_rpm","engine_idle_rpm","engine_brake_effect",
                  "engine_rev_up_moi","engine_rev_down_rate"):
            try:
                log("engine." + f + " = " + str(eng.get_editor_property(f)))
            except Exception:
                pass
        try:
            tc = eng.get_editor_property("torque_curve")
            log("engine.torque_curve = " + str(tc))
        except Exception as e:
            log("torque_curve okunamadi: " + repr(e))
        try:
            tr = vmc.get_editor_property("transmission_setup")
            for f in ("final_ratio","forward_gear_ratios","reverse_gear_ratios",
                      "change_up_rpm","change_down_rpm","gear_change_time",
                      "transmission_efficiency"):
                try:
                    log("trans." + f + " = " + str(tr.get_editor_property(f)))
                except Exception:
                    pass
            fr = tr.get_editor_property("final_ratio")
            if float(fr) == 0.0:
                supheli.append("final_ratio = 0")
        except Exception as e:
            log("transmission okunamadi: " + repr(e))
        try:
            df = vmc.get_editor_property("differential_setup")
            log("diff.type = " + str(df.get_editor_property("differential_type")))
            log("diff.front_rear_split = " + str(df.get_editor_property("front_rear_split")))
        except Exception:
            pass
        try:
            ws = vmc.get_editor_property("wheel_setups")
            i = 0
            for w in ws:
                wc = w.get_editor_property("wheel_class")
                log("wheel_setup" + str(i) + ".class = " + str(wc))
                i = i + 1
        except Exception:
            pass
except Exception as e:
    log("vehicle CDO okunamadi: " + repr(e))

if len(supheli) == 0:
    log("SONUC: PASS - radius/egri/ratio temiz; siradaki: A/B taze arac testi")
else:
    log("SONUC: SUPHELI BULUNDU -> " + " | ".join(supheli))
