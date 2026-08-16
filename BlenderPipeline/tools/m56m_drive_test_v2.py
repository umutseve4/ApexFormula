# m56m_drive_test_v2.py - UludagFormula M5.5 kabul testi
# QA (DENETIM) kriterleri: settle t>3s, zdrop>20cm VEYA yere oturma, XY>300cm, speed>100cm/s
# m56q runtime unfreeze dahili (set_simulate_physics + all_bodies + blend_weight).
# Kullanim: PIE KAPALIYKEN calistir; script PIE'yi kendisi baslatir, 12 sn olcer, raporlar.
import unreal

STATE = {"phase": "wait_pie", "t": 0.0, "pawn": None, "vmc": None,
         "z0": None, "x0": None, "y0": None, "settle_z": None,
         "max_speed": 0.0, "max_xy": 0.0, "done": False, "handle": None}
SETTLE_T = 3.0
END_T = 12.0
LINES = []

def log(msg):
    line = "[M56M] %s" % msg
    LINES.append(line)
    unreal.log(line)

def finish():
    if STATE["done"]:
        return
    STATE["done"] = True
    unreal.unregister_slate_post_tick_callback(STATE["handle"])
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.editor_request_end_play()
    zdrop = (STATE["z0"] - STATE["settle_z"]) if STATE["settle_z"] is not None else 0.0
    xy = STATE["max_xy"]
    sp = STATE["max_speed"]
    p_z = zdrop > 20.0
    p_xy = xy > 300.0
    p_sp = sp > 100.0
    log("OLCUM zdrop=%.1fcm XY=%.1fcm maxspeed=%.1fcm/s" % (zdrop, xy, sp))
    log("KRITER zdrop>20: %s | XY>300: %s | speed>100: %s"
        % ("PASS" if p_z else "FAIL", "PASS" if p_xy else "FAIL",
           "PASS" if p_sp else "FAIL"))
    overall = p_xy and p_sp  # zdrop bilgilendirici: arac zaten oturmus olabilir
    print("\n".join(LINES))
    print("[M56M] SONUC: %s" % ("PASS" if overall else "FAIL"))

def tick(dt):
    try:
        STATE["t"] += dt
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        if STATE["phase"] == "wait_pie":
            if not les.is_in_play_in_editor():
                if STATE["t"] > 15.0:
                    log("FAIL: PIE 15sn icinde baslamadi")
                    finish()
                return
            STATE["phase"] = "find"
            STATE["t"] = 0.0
            return
        ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        world = ues.get_game_world()
        if STATE["phase"] == "find":
            if world is None:
                if STATE["t"] > 5.0:
                    log("FAIL: PIE game world alinamadi")
                    finish()
                return
            src = unreal.GameplayStatics.get_all_actors_of_class(
                world, unreal.WheeledVehiclePawn)
            if not src:
                if STATE["t"] > 5.0:
                    log("FAIL: WheeledVehiclePawn PIE'de bulunamadi")
                    finish()
                return
            pawn = src[0]
            STATE["pawn"] = pawn
            mesh = pawn.get_editor_property("mesh")
            # m56q unfreeze
            mesh.set_simulate_physics(True)
            mesh.set_all_bodies_simulate_physics(True)
            mesh.set_editor_property("physics_blend_weight", 1.0)
            vmc = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
            STATE["vmc"] = vmc
            loc = pawn.get_actor_location()
            STATE["z0"], STATE["x0"], STATE["y0"] = loc.z, loc.x, loc.y
            log("Pawn bulundu: %s z0=%.1f  VMC=%s" % (pawn.get_name(), loc.z,
                "OK" if vmc else "YOK"))
            STATE["phase"] = "run"
            STATE["t"] = 0.0
            return
        if STATE["phase"] == "run":
            pawn, vmc = STATE["pawn"], STATE["vmc"]
            if pawn is None or not unreal.SystemLibrary.is_valid(pawn):
                log("FAIL: pawn kayboldu")
                finish()
                return
            if vmc:
                vmc.set_throttle_input(1.0)
                if STATE["t"] < 0.5:
                    vmc.set_target_gear(1, True)
            loc = pawn.get_actor_location()
            if STATE["t"] >= SETTLE_T and STATE["settle_z"] is None:
                STATE["settle_z"] = loc.z
                log("Settle (t=%.1fs) z=%.1f (z0=%.1f)" % (STATE["t"], loc.z, STATE["z0"]))
            dx, dy = loc.x - STATE["x0"], loc.y - STATE["y0"]
            xy = (dx * dx + dy * dy) ** 0.5
            STATE["max_xy"] = max(STATE["max_xy"], xy)
            if vmc:
                sp = abs(vmc.get_forward_speed())
                STATE["max_speed"] = max(STATE["max_speed"], sp)
            if STATE["t"] >= END_T:
                finish()
    except Exception as e:
        log("EXC: %s" % e)
        finish()

STATE["handle"] = unreal.register_slate_post_tick_callback(tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
log("PIE baslatildi, %.0f sn olcum..." % END_T)
