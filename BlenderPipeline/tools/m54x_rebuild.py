import unreal
w = unreal.EditorLevelLibrary.get_game_world()
P="=M54X= "
def log(s): unreal.log(P+s)
log("===== OTOMATIK KONTROL =====")
try:
    ps = unreal.get_default_object(unreal.PhysicsSettings)
    for cand in ["tick_physics_async","b_tick_physics_async","enable_async_physics"]:
        try:
            log("PhysicsSettings.%s = %s" % (cand, ps.get_editor_property(cand)))
        except Exception:
            pass
except Exception as e:
    log("PhysicsSettings HATA: %r" % e)
pawn=None
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Pawn):
    if "BP_AF_VehiclePawn" in a.get_name(): pawn=a
if pawn is None:
    log("PAWN YOK - Play basili mi?")
else:
    vmc = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    try:
        log("baslangic gear: current=%s target=%s" % (vmc.get_current_gear(), vmc.get_target_gear()))
    except Exception as e:
        log("gear oku HATA: %r" % e)
    try:
        es = vmc.get_editor_property("engine_setup")
        log("engine_setup max_rpm=%s idle=%s max_torque=%s" % (
            es.get_editor_property("max_rpm"),
            es.get_editor_property("engine_idle_rpm"),
            es.get_editor_property("max_torque")))
        vmc.set_editor_property("engine_setup", es)
        log("engine_setup geri-yazildi")
    except Exception as e:
        log("engine_setup HATA: %r" % e)
    try:
        ts = vmc.get_editor_property("transmission_setup")
        vmc.set_editor_property("transmission_setup", ts)
        log("transmission_setup geri-yazildi")
    except Exception as e:
        log("transmission_setup HATA: %r" % e)
    try:
        vmc.recreate_physics_state()
        log("recreate_physics_state OK")
    except Exception as e:
        log("recreate_physics_state HATA: %r" % e)
    try:
        vmc.set_requires_controller_for_inputs(False)
    except Exception: pass
    st={"t":0.0,"rpm":0.0,"fwd":0.0,"gmax":-9,"h":None}
    def tick(dt):
        st["t"]+=dt
        try:
            vmc.set_throttle_input(1.0)
            vmc.set_brake_input(0.0)
            vmc.set_handbrake_input(False)
        except Exception: pass
        try:
            g=vmc.get_current_gear()
            if g>st["gmax"]: st["gmax"]=g
        except Exception: pass
        try:
            r=vmc.get_engine_rotation_speed()
            if r>st["rpm"]: st["rpm"]=r
        except Exception: pass
        try:
            f=abs(vmc.get_forward_speed())
            if f>st["fwd"]: st["fwd"]=f
        except Exception: pass
        if st["t"]>=6.0:
            unreal.unregister_slate_post_tick_callback(st["h"])
            log("---- 6 sn bitti ----")
            log("rpm max = %.0f  fwd max = %.1f cm/s  gear max = %s" % (st["rpm"], st["fwd"], st["gmax"]))
            if st["rpm"]>1250.0 and st["fwd"]>50.0:
                log("SONUC: ARAC CALISTI - rebuild kok nedeni cozdu, kalici fix sirada")
            elif st["rpm"]>1250.0:
                log("SONUC: MOTOR UYANDI - aktarim katmanina gec")
            else:
                log("SONUC: REBUILD ETKISIZ - motor sim tick almiyor; async physics / component yeniden kurulum sirada")
    st["h"]=unreal.register_slate_post_tick_callback(tick)
    log("6 sn gaz testi basladi - DOKUNMA")
