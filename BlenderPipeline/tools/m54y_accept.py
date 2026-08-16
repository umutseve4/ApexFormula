import unreal
w = unreal.EditorLevelLibrary.get_game_world()
P="=M54Y= "
def log(s): unreal.log(P+s)
try:
    ps = unreal.get_default_object(unreal.PhysicsSettings)
    log("tick_physics_async = %s" % ps.get_editor_property("tick_physics_async"))
except Exception as e:
    log("ayar oku HATA: %r" % e)
pawn=None
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Pawn):
    if "BP_AF_VehiclePawn" in a.get_name(): pawn=a
if pawn is None:
    log("PAWN YOK - Play basili mi?")
else:
    vmc = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    try: vmc.set_requires_controller_for_inputs(False)
    except Exception: pass
    st={"t":0.0,"rpm":0.0,"fwd":0.0,"g":-9,"h":None}
    def tick(dt):
        st["t"]+=dt
        try:
            vmc.set_throttle_input(1.0)
            vmc.set_brake_input(0.0)
            vmc.set_handbrake_input(False)
        except Exception: pass
        try:
            r=vmc.get_engine_rotation_speed()
            if r>st["rpm"]: st["rpm"]=r
        except Exception: pass
        try:
            f=abs(vmc.get_forward_speed())
            if f>st["fwd"]: st["fwd"]=f
        except Exception: pass
        try:
            g=vmc.get_current_gear()
            if g>st["g"]: st["g"]=g
        except Exception: pass
        if st["t"]>=6.0:
            unreal.unregister_slate_post_tick_callback(st["h"])
            log("===== OTOMATIK KONTROL =====")
            log("rpm max = %.0f  fwd max = %.1f cm/s  gear max = %s" % (st["rpm"], st["fwd"], st["g"]))
            if st["rpm"]>1250.0 and st["fwd"]>100.0:
                log("SONUC: PASS - ARAC SURUYOR, M5.4f kabul")
            elif st["rpm"]>1250.0:
                log("SONUC: MOTOR CANLANDI ama arac yavas - aktarim/surtunme katmani")
            else:
                log("SONUC: FAIL - async fix de etkisiz, component yeniden kurulum turu")
    st["h"]=unreal.register_slate_post_tick_callback(tick)
    log("6 sn gaz testi basladi - DOKUNMA")
