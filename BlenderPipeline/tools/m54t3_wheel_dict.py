import unreal
w = unreal.EditorLevelLibrary.get_game_world()
acts = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
p = None
for a in acts:
    p = a
    break
mv = p.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
print("=M54T3= ===== OTOMATIK KONTROL =====")
print("=M54T3= pawn z = %.1f" % p.get_actor_location().z)
i = 0
while i < 4:
    st = mv.get_wheel_state(i)
    try:
        print("=M54T3= teker%d dict = %s" % (i, st.to_dict()))
    except Exception as e:
        print("=M54T3= teker%d dict hatasi: %s" % (i, e))
    try:
        print("=M54T3= teker%d tuple = %s" % (i, st.to_tuple()))
    except Exception as e:
        print("=M54T3= teker%d tuple hatasi: %s" % (i, e))
    i = i + 1
