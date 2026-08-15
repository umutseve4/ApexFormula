# m54f_drive_test.py v2 - M5.4f PIE surus kabul testi (D-092 kriterleri)
# v1 FAIL analizi: PIE basladi ama get_game_world() tespiti calismadi; ayrica
# otomatik baslatma zinciri PIE'yi kararsiz yeniden baslatti. v2 degisiklikleri:
#   1) Otomatik PIE baslatma YOK -> script calisir, SEN viewport'tan Play'e basarsin.
#   2) Dunya tespiti cok-problu: UnrealEditorSubsystem.get_game_world,
#      EditorLevelLibrary.get_game_world, LevelEditorSubsystem.is_in_play_in_editor.
#   3) WAIT_PIE sirasinda 5 sn'de bir HEARTBEAT satiri: her probun dondurdugu deger
#      loglanir -> FAIL olursa kok neden logda gorunur.
# Kosum: UE Output Log ->  py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54f_drive_test.py"
# Fazlar (girisler dogrudan ChaosWheeledVehicleMovementComponent'e verilir):
#   SETTLE 0-5s   : giris yok        -> Z bandi +-50 cm
#   FWD    5-10s  : throttle=1.0     -> yatay yer degistirme >= 1000 cm (10 m)
#   STEER  10-13s : thr=0.6 steer=1  -> yaw degisimi >= 10 derece
#   BRAKE  13-17s : thr=0 brake=1    -> hiz, fren basindaki hizin %20'sine iner (veya <=200 cm/s)

import unreal

MAP_PATH = "/Game/vehicle/Map_AF_DriveTest"
S = {
    "t": 0.0, "phase": "WAIT_PIE", "wait": 0.0, "hb_next": 0.0,
    "z0": None, "z_min": None, "z_max": None,
    "fwd_start": None, "yaw_start": None,
    "brake_v0": None,
    "results": [], "handle": None, "done": False,
    "err_seen": set(),
}

def log(msg):
    unreal.log("[M54F] " + msg)

def log_err_once(tag, e):
    key = tag + ":" + repr(e)
    if key not in S["err_seen"]:
        S["err_seen"].add(key)
        log("ERR %s -> %r" % (tag, e))

def probe_world():
    """PIE dunyasini birden fazla API ile ara; (world, kaynak_adi) dondur."""
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if w:
            return w, "UnrealEditorSubsystem"
    except Exception as e:
        log_err_once("UnrealEditorSubsystem.get_game_world", e)
    try:
        w = unreal.EditorLevelLibrary.get_game_world()
        if w:
            return w, "EditorLevelLibrary"
    except Exception as e:
        log_err_once("EditorLevelLibrary.get_game_world", e)
    return None, "-"

def probe_pie_flag():
    try:
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        return str(les.is_in_play_in_editor())
    except Exception as e:
        log_err_once("is_in_play_in_editor", e)
        return "API-YOK"

def get_vehicle(world):
    try:
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    except Exception as e:
        log_err_once("get_player_pawn", e)
        return None, None
    if not pawn:
        return None, None
    try:
        comp = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    except Exception as e:
        log_err_once("get_component_by_class", e)
        return pawn, None
    return pawn, comp

def add_result(name, ok, detail):
    S["results"].append((name, ok, detail))
    log("%s %s  %s" % (name, "PASS" if ok else "FAIL", detail))

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
        if all_ok else "HEARTBEAT satirlariyla birlikte ciktiyi raporla"))
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        log("PIE'yi elle durdur (Esc).")

def tick(dt):
    if S["done"]:
        return
    world, src = probe_world()

    if S["phase"] == "WAIT_PIE":
        S["wait"] += dt
        if world:
            pawn, comp = get_vehicle(world)
            if pawn and comp:
                S["phase"] = "SETTLE"
                S["t"] = 0.0
                z = pawn.get_actor_location().z
                S["z0"] = S["z_min"] = S["z_max"] = z
                log("PIE dunyasi bulundu (kaynak=%s); pawn=%s z0=%.1f -> SETTLE" % (src, pawn.get_name(), z))
                return
        if S["wait"] >= S["hb_next"]:
            S["hb_next"] = S["wait"] + 5.0
            pawn, comp = get_vehicle(world) if world else (None, None)
            log("HEARTBEAT t=%.0fs  world=%s(kaynak=%s)  pie_flag=%s  pawn=%s  comp=%s"
                % (S["wait"], world.get_name() if world else "None", src,
                   probe_pie_flag(),
                   pawn.get_name() if pawn else "None",
                   type(comp).__name__ if comp else "None"))
        if S["wait"] > 180.0:
            add_result("SETTLE", False, "PIE/pawn 180s icinde bulunamadi - HEARTBEAT satirlarina bak")
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
    log(">>> SIMDI viewport ustundeki Play'e BIR KEZ bas. Script 180 sn bekliyor;")
    log(">>> 5 sn'de bir HEARTBEAT satiri basar, test ~17 sn surer ve kendini raporlar.")

main()
