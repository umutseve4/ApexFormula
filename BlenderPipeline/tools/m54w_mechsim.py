import unreal
w = unreal.EditorLevelLibrary.get_game_world()
P="=M54W= "
def log(s): unreal.log(P+s)
pawn=None
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Pawn):
    if "BP_AF_VehiclePawn" in a.get_name(): pawn=a
if pawn is None:
    log("PAWN YOK - Play basili mi?")
else:
    vmc = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    log("===== OTOMATIK KONTROL =====")
    flags=["mechanical_sim_enabled","suspension_enabled","wheel_friction_enabled"]
    vals={}
    for f in flags:
        try:
            vals[f]=vmc.get_editor_property(f)
            log("%s = %s" % (f, vals[f]))
        except Exception as e:
            vals[f]=None
            log("%s OKUNAMADI: %r" % (f, e))
    fixed=[]
    for f in flags:
        if vals[f] is False:
            try:
                vmc.set_editor_property(f, True)
                fixed.append(f)
                log("FIX: %s -> True" % f)
            except Exception as e:
                log("FIX HATA %s: %r" % (f, e))
    if fixed:
        try:
            vmc.recreate_physics_state()
            log("recreate_physics_state OK")
        except Exception as e:
            log("recreate_physics_state HATA: %r" % e)
    try:
        vmc.set_requires_controller_for_inputs(False)
    except Exception: pass
    st={"t":0.0,"rpm":0.0,"fwd":0.0,"h":None}
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
        if st["t"]>=6.0:
            unreal.unregister_slate_post_tick_callback(st["h"])
            log("---- 6 sn bitti ----")
            log("duzeltilen bayrak: %s" % (", ".join(fixed) if fixed else "YOK"))
            log("rpm max = %.0f   fwd max = %.1f cm/s" % (st["rpm"], st["fwd"]))
            if st["rpm"]>1250.0 and st["fwd"]>50.0:
                log("SONUC: ARAC CALISTI - kok neden bulundu, kalici CDO fix sirada")
            elif st["rpm"]>1250.0:
                log("SONUC: MOTOR UYANDI ama arac yavas - aktarim katmanina bak")
            elif fixed:
                log("SONUC: bayrak acildi ama RPM hala kilitli - sim yeniden kurulmadi, restart+CDO fix dene")
            else:
                log("SONUC: bayraklar zaten acik - engine_setup runtime rebuild sirada")
    st["h"]=unreal.register_slate_post_tick_callback(tick)
    log("6 sn gaz testi basladi - DOKUNMA")
