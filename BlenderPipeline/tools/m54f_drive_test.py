# m54f_drive_test.py - M5.4f PIE surus kabul testi (D-092 kriterleri)
# Kosum: UE Output Log ->  py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54f_drive_test.py"
# Akis: haritayi yukler -> PIE baslatmayi dener (olmazsa Play'e basmani ister)
#       -> tick callback ile faz makinesi kosar, sonunda OTOMATIK KONTROL basar.
# Fazlar (girisler dogrudan ChaosWheeledVehicleMovementComponent'e verilir):
#   SETTLE 0-5s   : giris yok        -> Z bandi +-50 cm
#   FWD    5-10s  : throttle=1.0     -> yatay yer degistirme >= 1000 cm (10 m)
#   STEER  10-13s : thr=0.6 steer=1  -> yaw degisimi >= 10 derece
#   BRAKE  13-17s : thr=0 brake=1    -> hiz, fren basindaki hizin %20'sinin altina iner
# NOT: klavye (W/A/S/D) zinciri ayrica 1 manuel PIE turu + screenshot ile kanitlanir.

import unreal

MAP_PATH = "/Game/vehicle/Map_AF_DriveTest"
S = {
    "t": 0.0, "phase": "WAIT_PIE", "wait": 0.0,
    "z0": None, "z_min": None, "z_max": None,
    "fwd_start": None, "yaw_start": None,
    "brake_v0": None, "v_end": None,
    "results": [], "handle": None, "done": False,
}

def log(msg):
    unreal.log("[M54F] " + msg)

def get_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None

def get_vehicle(world):
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    if not pawn:
        return None, None
    comp = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    return pawn, comp

def add_result(name, ok, detail):
    S["results"].append((name, ok, detail))
    log(("%s %s  %s") % (name, "PASS" if ok else "FAIL", detail))

def finish():
    S["done"] = True
    if S["handle"] is not None:
        unreal.unregister_slate_post_tick_callback(S["handle"])
        S["handle"] = None
    log("===== OTOMATIK KONTROL =====")
    all_ok = all(ok for _, ok, _ in S["results"]) and len(S["results"]) == 4
    for name, ok, detail in S["results"]:
        log("%-8s : %s  (%s)" % (name, "PASS" if ok else "FAIL", detail))
    log("SONUC %s - %s" % ("PASS" if all_ok else "FAIL",
        "M5.4f otomatik kisim tamam; simdi manuel W/A/S/D turu + screenshot"
        if all_ok else "kriter dusuruldu, cikti ile birlikte raporla"))
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        log("PIE'yi elle durdur (Esc).")

def tick(dt):
    if S["done"]:
        return
    world = get_world()

    if S["phase"] == "WAIT_PIE":
        S["wait"] += dt
        if world:
            pawn, comp = get_vehicle(world)
            if pawn and comp:
                S["phase"] = "SETTLE"
                S["t"] = 0.0
                z = pawn.get_actor_location().z
                S["z0"] = S["z_min"] = S["z_max"] = z
                log("PIE dunyasi bulundu; pawn=%s  z0=%.1f  -> SETTLE" % (pawn.get_name(), z))
        elif S["wait"] > 120.0:
            add_result("SETTLE", False, "PIE 120s icinde baslamadi")
            add_result("FWD", False, "-"); add_result("STEER", False, "-")
            add_result("BRAKE", False, "-")
            finish()
        return

    pawn, comp = get_vehicle(world) if world else (None, None)
    if not (world and pawn and comp):
        add_result("SETTLE", False, "PIE/pawn kayboldu (t=%.1f)" % S["t"])
        finish()
        return

    S["t"] += dt
    t = S["t"]
    loc = pawn.get_actor_location()
    yaw = pawn.get_actor_rotation().yaw
    speed = abs(comp.get_forward_speed())  # cm/s

    if S["phase"] == "SETTLE":
        comp.set_throttle_input(0.0); comp.set_brake_input(0.0); comp.set_steering_input(0.0)
        S["z_min"] = min(S["z_min"], loc.z); S["z_max"] = max(S["z_max"], loc.z)
        if t >= 5.0:
            dev = max(abs(S["z_max"] - S["z0"]), abs(S["z_min"] - S["z0"]))
            add_result("SETTLE", dev <= 50.0, "z sapma=%.1f cm (<=50)" % dev)
            S["fwd_start"] = unreal.Vector(loc.x, loc.y, loc.z)
            S["phase"] = "FWD"

    elif S["phase"] == "FWD":
        comp.set_throttle_input(1.0); comp.set_brake_input(0.0); comp.set_steering_input(0.0)
        if t >= 10.0:
            dx = loc.x - S["fwd_start"].x; dy = loc.y - S["fwd_start"].y
            dist = (dx * dx + dy * dy) ** 0.5
            add_result("FWD", dist >= 1000.0, "yatay yer degistirme=%.0f cm (>=1000)" % dist)
            S["yaw_start"] = yaw
            S["phase"] = "STEER"

    elif S["phase"] == "STEER":
        comp.set_throttle_input(0.6); comp.set_brake_input(0.0); comp.set_steering_input(1.0)
        if t >= 13.0:
            dyaw = abs(((yaw - S["yaw_start"]) + 180.0) % 360.0 - 180.0)
            add_result("STEER", dyaw >= 10.0, "yaw degisimi=%.1f derece (>=10)" % dyaw)
            S["brake_v0"] = max(speed, 1.0)
            S["phase"] = "BRAKE"

    elif S["phase"] == "BRAKE":
        comp.set_throttle_input(0.0); comp.set_steering_input(0.0); comp.set_brake_input(1.0)
        if t >= 17.0:
            ratio = speed / S["brake_v0"]
            add_result("BRAKE", ratio <= 0.2 or speed <= 200.0,
                       "hiz %.0f -> %.0f cm/s (oran %.2f, <=0.20 veya <=200)" % (S["brake_v0"], speed, ratio))
            finish()

def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP_PATH)
    log("Harita yuklendi: %s" % MAP_PATH)
    S["handle"] = unreal.register_slate_post_tick_callback(tick)
    started = False
    for fn in ("editor_request_begin_play", "editor_play_in_viewport"):
        try:
            getattr(les, fn)()
            started = True
            log("PIE otomatik baslatildi (%s)." % fn)
            break
        except Exception:
            continue
    if not started:
        log("PIE otomatik baslatilamadi -> viewport ustundeki Play'e SEN bas; script bekliyor (120s).")

main()
