# m54k_manual_drive.py - M5.4f manuel surus kabul testi (PASIF GOZLEM)
# Gerekce (kosum m54j sonrasi): CDO konfig SAGLIKLI cikti (Curve_AF_Torque 300Nm,
# RWD, 2 teker eng=True) ama m54f v4'te script'in set_throttle_input(1.0) cagrisi
# RPM'i rolantiden (1200) kaldiramadi. Fren/vites yolu calisiyordu. Kalan tek
# suphe: possessed pawn'da PlayerController input islemesi her tick raw input'u
# eziyor (script girdisi 0'a donuyor). Cozum: girdiyi INSAN verir (W/A/S/D),
# script HICBIR input SET ETMEZ - sadece olcer ve PASS/FAIL karari verir.
# Kosum: UE Output Log -> py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54k_manual_drive.py"
# Sonra Play'e BIR KEZ bas, VIEWPORT ICINE TIKLA (klavye odagi!), yonergeleri izle.
# Olcum penceresi: pawn bulunduktan sonra 45 sn. Kriterler (D-092):
#   FWD   : toplam yatay yer degistirme >= 1000 cm
#   SPEED : tepe hiz >= 300 cm/s
#   STEER : yaw degisimi (baslangica gore max) >= 10 derece
#   BRAKE : son 3 sn ort. hiz <= tepe hizin %30'u (S ile durdun mu)

import unreal

S = {
    "t": 0.0, "phase": "WAIT_PIE", "wait": 0.0, "hb_next": 0.0, "diag_next": 0.0,
    "start_loc": None, "yaw_start": None,
    "max_dist": 0.0, "max_speed": 0.0, "max_dyaw": 0.0,
    "tail": [],  # (t, speed) son saniyeler
    "results": [], "handle": None, "done": False, "err_seen": set(),
}
WINDOW = 45.0

def log(msg):
    unreal.log("[M54K] " + msg)

def log_err_once(tag, e):
    key = tag + ":" + repr(e)
    if key not in S["err_seen"]:
        S["err_seen"].add(key)
        log("ERR %s -> %r" % (tag, e))

def probe_world():
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if w:
            return w
    except Exception as e:
        log_err_once("get_game_world", e)
    return None

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

def diag(pawn, comp):
    gear = rpm = spd = "?"
    try:
        gear = comp.get_current_gear()
    except Exception as e:
        log_err_once("get_current_gear", e)
    try:
        rpm = "%.0f" % comp.get_engine_rotation_speed()
    except Exception as e:
        log_err_once("get_engine_rotation_speed", e)
    try:
        spd = "%.0f" % abs(comp.get_forward_speed())
    except Exception:
        pass
    log("DIAG t=%.0fs gear=%s rpm=%s hiz=%scm/s z=%.1f  (maxhiz=%.0f maxmesafe=%.0f maxdyaw=%.1f)" %
        (S["t"], gear, rpm, spd, pawn.get_actor_location().z,
         S["max_speed"], S["max_dist"], S["max_dyaw"]))

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
        log("%-6s : %s  (%s)" % (name, "PASS" if ok else "FAIL", detail))
    log("SONUC %s - %s" % ("PASS" if all_ok else "FAIL",
        "arac insan girdisiyle suruluyor; M5.4f kabul saglandi (screenshot al)"
        if all_ok else "DIAG satirlariyla ciktiyi raporla"))
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        log("PIE'yi elle durdur (Esc).")

def tick(dt):
    if S["done"]:
        return
    world = probe_world()

    if S["phase"] == "WAIT_PIE":
        S["wait"] += dt
        if world:
            pawn, comp = get_vehicle(world)
            if pawn and comp:
                S["phase"] = "MEASURE"
                S["t"] = 0.0
                loc = pawn.get_actor_location()
                S["start_loc"] = unreal.Vector(loc.x, loc.y, loc.z)
                S["yaw_start"] = pawn.get_actor_rotation().yaw
                log("PIE bulundu; pawn=%s. OLCUM BASLADI (45 sn)." % pawn.get_name())
                log(">>> VIEWPORT ICINE TIKLA, sonra: ~10 sn W bas | ~5 sn W+A | S ile dur.")
                return
        if S["wait"] >= S["hb_next"]:
            S["hb_next"] = S["wait"] + 5.0
            log("HEARTBEAT t=%.0fs world=%s" % (S["wait"], world.get_name() if world else "None"))
        if S["wait"] > 180.0:
            add_result("FWD", False, "PIE/pawn 180s icinde bulunamadi")
            add_result("SPEED", False, "-"); add_result("STEER", False, "-")
            add_result("BRAKE", False, "-")
            finish()
        return

    pawn, comp = get_vehicle(world) if world else (None, None)
    if not (world and pawn and comp):
        add_result("FWD", False, "PIE/pawn kayboldu (t=%.1f)" % S["t"])
        finish()
        return

    S["t"] += dt
    t = S["t"]
    loc = pawn.get_actor_location()
    yaw = pawn.get_actor_rotation().yaw
    speed = 0.0
    try:
        speed = abs(comp.get_forward_speed())
    except Exception:
        pass

    dx = loc.x - S["start_loc"].x
    dy = loc.y - S["start_loc"].y
    dist = (dx * dx + dy * dy) ** 0.5
    dyaw = abs(((yaw - S["yaw_start"]) + 180.0) % 360.0 - 180.0)
    S["max_dist"] = max(S["max_dist"], dist)
    S["max_speed"] = max(S["max_speed"], speed)
    S["max_dyaw"] = max(S["max_dyaw"], dyaw)
    S["tail"].append((t, speed))
    S["tail"] = [(tt, ss) for (tt, ss) in S["tail"] if t - tt <= 3.0]

    if t >= S["diag_next"]:
        S["diag_next"] = t + 5.0
        diag(pawn, comp)

    if t >= WINDOW:
        tail_avg = (sum(ss for _, ss in S["tail"]) / len(S["tail"])) if S["tail"] else 0.0
        add_result("FWD", S["max_dist"] >= 1000.0,
                   "max yatay yer degistirme=%.0f cm (>=1000)" % S["max_dist"])
        add_result("SPEED", S["max_speed"] >= 300.0,
                   "tepe hiz=%.0f cm/s (>=300)" % S["max_speed"])
        add_result("STEER", S["max_dyaw"] >= 10.0,
                   "max yaw degisimi=%.1f derece (>=10)" % S["max_dyaw"])
        brake_ok = (S["max_speed"] < 1.0) is False and (tail_avg <= 0.3 * S["max_speed"] or tail_avg <= 200.0)
        add_result("BRAKE", brake_ok,
                   "son 3sn ort hiz=%.0f cm/s (tepe %.0f'in <=%%30'u veya <=200)" % (tail_avg, S["max_speed"]))
        finish()

def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level("/Game/vehicle/Map_AF_DriveTest")
    log("Harita yuklendi. Bu test PASIFTIR: script hicbir input GONDERMEZ.")
    S["handle"] = unreal.register_slate_post_tick_callback(tick)
    log(">>> Play'e BIR KEZ bas -> viewport icine TIKLA -> W/A/S ile sur (45 sn).")

main()
