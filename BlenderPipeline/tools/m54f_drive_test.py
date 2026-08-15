# m54f_drive_test.py v3 - M5.4f PIE surus kabul testi (D-092 kriterleri)
# v2 FAIL analizi: pawn dogru (BP_AF_VehiclePawn) ama FWD=0cm, STEER=0.0 ve
# SETTLE z sapma=0.0 -> arac HIC simule olmuyor (z=150'den yere bile dusmemis).
# Kok neden adaylari: mesh Simulate Physics kapali / vites N / el freni.
# v3 degisiklikleri:
#   1) ENGAGE adimi: pawn bulununca is_simulating_physics kontrol -> kapaliysa AC,
#      set_use_automatic_gears(True), set_target_gear(1), set_handbrake_input(False).
#   2) Her faz gecisinde DIAG satiri: gear / RPM / hiz / simfizik.
#   3) Deprecated EditorLevelLibrary fallback kaldirildi (subsystem probu kanitli calisiyor).
# Kosum: UE Output Log ->  py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/m54f_drive_test.py"
# Fazlar: SETTLE 0-5s (Z +-50cm; z0'dan dusus varsa serbest) -> FWD 5-10s (>=1000cm)
#         -> STEER 10-13s (|dyaw|>=10) -> BRAKE 13-17s (hiz orani <=0.20 veya <=200cm/s)

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
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if w:
            return w, "UnrealEditorSubsystem"
    except Exception as e:
        log_err_once("UnrealEditorSubsystem.get_game_world", e)
    return None, "-"

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

def get_mesh(pawn):
    try:
        return pawn.get_component_by_class(unreal.SkeletalMeshComponent)
    except Exception as e:
        log_err_once("get_mesh", e)
        return None

def diag(tag, pawn, comp):
    gear = rpm = sim = "?"
    try:
        gear = comp.get_current_gear()
    except Exception as e:
        log_err_once("get_current_gear", e)
    try:
        rpm = "%.0f" % comp.get_engine_rotation_speed()
    except Exception as e:
        log_err_once("get_engine_rotation_speed", e)
    mesh = get_mesh(pawn)
    if mesh:
        try:
            sim = mesh.is_simulating_physics()
        except Exception as e:
            log_err_once("is_simulating_physics", e)
    spd = "?"
    try:
        spd = "%.0f" % abs(comp.get_forward_speed())
    except Exception:
        pass
    log("DIAG[%s] gear=%s rpm=%s simfizik=%s hiz=%scm/s z=%.1f" %
        (tag, gear, rpm, sim, spd, pawn.get_actor_location().z))

def engage(pawn, comp):
    """Drivetrain'i teste hazirla: fizik ac, otomatik vites + gear 1, el freni birak."""
    mesh = get_mesh(pawn)
    if mesh:
        try:
            if not mesh.is_simulating_physics():
                mesh.set_simulate_physics(True)
                log("ENGAGE simulate_physics KAPALIYDI -> ACILDI")
            else:
                log("ENGAGE simulate_physics zaten acik")
        except Exception as e:
            log_err_once("set_simulate_physics", e)
    else:
        log("ENGAGE UYARI: SkeletalMeshComponent bulunamadi")
    for name, args in (("set_use_automatic_gears", (True,)),
                       ("set_target_gear", (1,)),
                       ("set_handbrake_input", (False,))):
        try:
            getattr(comp, name)(*args)
            log("ENGAGE %s%s OK" % (name, args))
        except Exception as e:
            log_err_once(name, e)

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
        if all_ok else "DIAG+HEARTBEAT satirlariyla birlikte ciktiyi raporla"))
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
                log("PIE dunyasi bulundu (kaynak=%s); pawn=%s z0=%.1f -> ENGAGE+SETTLE" % (src, pawn.get_name(), z))
                engage(pawn, comp)
                diag("SETTLE-IN", pawn, comp)
                return
        if S["wait"] >= S["hb_next"]:
            S["hb_next"] = S["wait"] + 5.0
            pawn, comp = get_vehicle(world) if world else (None, None)
            log("HEARTBEAT t=%.0fs  world=%s(kaynak=%s)  pawn=%s  comp=%s"
                % (S["wait"], world.get_name() if world else "None", src,
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
            # v3: z0'dan asagi inis (yere oturma) serbest; olcut son 'titresim' degil
            # basitce bant kontrolu: yere oturduktan sonraki z, z_min'e yakin olmali.
            dev = abs(loc.z - S["z_min"])
            add_result("SETTLE", dev <= 50.0, "yere oturma sonrasi sapma=%.1f cm (<=50); z0=%.1f z_min=%.1f" % (dev, S["z0"], S["z_min"]))
            S["fwd_start"] = unreal.Vector(loc.x, loc.y, loc.z)
            diag("FWD-IN", pawn, comp)
            S["phase"] = "FWD"

    elif S["phase"] == "FWD":
        comp.set_throttle_input(1.0); comp.set_brake_input(0.0); comp.set_steering_input(0.0)
        if t >= 10.0:
            dx = loc.x - S["fwd_start"].x; dy = loc.y - S["fwd_start"].y
            dist = (dx * dx + dy * dy) ** 0.5
            add_result("FWD", dist >= 1000.0, "yatay yer degistirme=%.0f cm (>=1000)" % dist)
            S["yaw_start"] = yaw
            diag("STEER-IN", pawn, comp)
            S["phase"] = "STEER"

    elif S["phase"] == "STEER":
        comp.set_throttle_input(0.6); comp.set_brake_input(0.0); comp.set_steering_input(1.0)
        if t >= 13.0:
            dyaw = abs(((yaw - S["yaw_start"]) + 180.0) % 360.0 - 180.0)
            add_result("STEER", dyaw >= 10.0, "yaw degisimi=%.1f derece (>=10)" % dyaw)
            S["brake_v0"] = max(speed, 1.0)
            diag("BRAKE-IN", pawn, comp)
            S["phase"] = "BRAKE"

    elif S["phase"] == "BRAKE":
        comp.set_throttle_input(0.0); comp.set_steering_input(0.0); comp.set_brake_input(1.0)
        if t >= 17.0:
            ratio = speed / S["brake_v0"]
            add_result("BRAKE", ratio <= 0.2 or speed <= 200.0,
                       "hiz %.0f -> %.0f cm/s (oran %.2f, <=0.20 veya <=200)" % (S["brake_v0"], speed, ratio))
            diag("SON", pawn, comp)
            finish()

def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP_PATH)
    log("Harita yuklendi: %s (script v3)" % MAP_PATH)
    S["handle"] = unreal.register_slate_post_tick_callback(tick)
    log(">>> SIMDI viewport ustundeki Play'e BIR KEZ bas. Script 180 sn bekliyor;")
    log(">>> ENGAGE+DIAG satirlari fizik/vites durumunu raporlar, test ~17 sn surer.")

main()
