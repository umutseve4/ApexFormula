import unreal
w = unreal.EditorLevelLibrary.get_game_world()
P="=M54V= "
def log(s): unreal.log(P+s)
pawn=None
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Pawn):
    if "BP_AF_VehiclePawn" in a.get_name(): pawn=a
if pawn is None:
    log("PAWN YOK - Play basili mi?")
else:
    vmc = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    log("===== OTOMATIK KONTROL =====")
    try:
        vmc.set_requires_controller_for_inputs(False)
        log("requires_controller_for_inputs=False SET EDILDI")
    except Exception as e:
        log("requires_controller set HATA: %r" % e)
    try:
        for i,s in enumerate(vmc.get_editor_property("wheel_setups")):
            cls = s.get_editor_property("wheel_class")
            cdo = unreal.get_default_object(cls)
            log("setup%d %s axle=%s" % (i, cls.get_name(), str(cdo.get_editor_property("axle_type"))))
    except Exception as e:
        log("setup dump HATA: %r" % e)
    try:
        for i,wh in enumerate(vmc.get_editor_property("wheels")):
            try: ax = str(wh.get_editor_property("axle_type"))
            except Exception: ax = "OKUNAMADI"
            log("runtime teker%d axle=%s" % (i, ax))
    except Exception as e:
        log("runtime wheels HATA: %r" % e)
    st={"t":0.0,"thr":-99.0,"brk":-99.0,"hbk":-99.0,"rpm":0.0,"fwd":0.0,"h":None,"err":0}
    def rd(prop):
        try: return float(vmc.get_editor_property(prop))
        except Exception: return -99.0
    def tick(dt):
        st["t"]+=dt
        try:
            vmc.set_throttle_input(1.0)
            vmc.set_brake_input(0.0)
            vmc.set_handbrake_input(False)
        except Exception as e:
            if st["err"]==0: log("input set HATA: %r" % e)
            st["err"]=1
        v=rd("throttle_input")
        if v>st["thr"]: st["thr"]=v
        v=rd("brake_input")
        if v>st["brk"]: st["brk"]=v
        v=rd("handbrake_input")
        if v>st["hbk"]: st["hbk"]=v
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
            log("throttle echo max = %s" % st["thr"])
            log("brake echo max    = %s" % st["brk"])
            log("handbrake echo max= %s" % st["hbk"])
            log("rpm max = %.0f   fwd max = %.1f cm/s" % (st["rpm"], st["fwd"]))
            if st["thr"]==-99.0:
                log("NOT: echo okunamadi (API gap) - karari RPM verir")
            if st["thr"]!=-99.0 and st["thr"]<0.5:
                log("SONUC: GAZ SIFIRLANIYOR - kontrolcu/BP katmani her tick eziyor")
            elif st["brk"]>0.1 or st["hbk"]>0.1:
                log("SONUC: FREN/ELFRENI TAKILI - kilit kaynagi bu")
            elif st["rpm"]<=1250.0:
                log("SONUC: MOTOR SIM ICI OLU - siradaki: mech-sim rebuild")
            else:
                log("SONUC: RPM YUKSELIYOR - tork-teker aktarim katmanina gec")
    st["h"]=unreal.register_slate_post_tick_callback(tick)
    log("6 sn zorla-gaz testi basladi - DOKUNMA")
