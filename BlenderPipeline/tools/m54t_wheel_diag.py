import unreal
w = unreal.EditorLevelLibrary.get_game_world()
pawns = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
pawn = None
for a in pawns:
    pawn = a
    break
if pawn is None:
    unreal.log("=M54T= FAIL - pawn yok, PIE acik mi?")
else:
    comp = pawn.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    mesh = pawn.get_component_by_class(unreal.SkeletalMeshComponent)
    loc = pawn.get_actor_location()
    unreal.log("=M54T= ===== OTOMATIK KONTROL =====")
    unreal.log("=M54T= pawn z = {:.1f}".format(loc.z))
    comp.set_throttle_input(1.0)
    n = 4
    i = 0
    while i < n:
        try:
            ws = comp.get_wheel_state(i)
            ic = ws.get_editor_property("in_contact")
            ns = ws.get_editor_property("normalized_suspension_length")
            sf = ws.get_editor_property("spring_force")
            sk = ws.get_editor_property("is_skidding")
            unreal.log("=M54T= teker{} temas={} susp_norm={:.2f} yay={:.0f} kayma={}".format(i, ic, ns, sf, sk))
        except Exception as e:
            unreal.log("=M54T= teker{} okunamadi: {}".format(i, e))
        i = i + 1
    comp.set_throttle_input(0.0)
