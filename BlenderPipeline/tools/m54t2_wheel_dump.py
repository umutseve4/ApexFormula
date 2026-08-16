import unreal
w = unreal.EditorLevelLibrary.get_game_world()
pawns = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.WheeledVehiclePawn)
p = None
for a in pawns:
    p = a
    break
if p is None:
    print("=M54T2= FAIL - PIE acik degil, once Play")
else:
    mc = p.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
    loc = p.get_actor_location()
    print("=M54T2= ===== OTOMATIK KONTROL =====")
    print("=M54T2= pawn z = %.1f" % loc.z)
    names = ""
    for nm in dir(unreal.WheelStatus):
        if nm.startswith("_"):
            continue
        names = names + nm + " "
    print("=M54T2= WheelStatus alanlari: " + names)
    i = 0
    while i < 4:
        ws = None
        try:
            ws = mc.get_wheel_state(i)
        except Exception as e:
            print("=M54T2= get_wheel_state hata: " + str(e))
        if ws is not None:
            print("=M54T2= teker%d durum: %s" % (i, str(ws)))
        i = i + 1
