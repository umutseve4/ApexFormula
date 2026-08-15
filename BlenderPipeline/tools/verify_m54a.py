# verify_m54a.py - D-092 M5.4a kabul kontrolu
# ChaosVehiclesPlugin etkin mi? Sinif yukleme testiyle dogrular.
# Kosum: UE Output Log ->  py "C:/Users/umuts/Documents/UludagFormula/BlenderPipeline/tools/verify_m54a.py"
import unreal

print("===== OTOMATIK KONTROL =====")

pawn_cls = unreal.load_class(None, "/Script/ChaosVehicles.WheeledVehiclePawn")
wheel_cls = unreal.load_class(None, "/Script/ChaosVehicles.ChaosVehicleWheel")
move_cls = unreal.load_class(None, "/Script/ChaosVehicles.ChaosWheeledVehicleMovementComponent")

def rep(name, cls):
    ok = cls is not None
    print("%-6s: %s - %s %s" % (name, "PASS" if ok else "FAIL",
                                name, "yuklendi" if ok else "yok"))
    return ok

ok1 = rep("PAWN", pawn_cls)
ok2 = rep("WHEEL", wheel_cls)
ok3 = rep("MOVE", move_cls)

if ok1 and ok2 and ok3:
    print("SONUC : PASS - M5.4a tamam; M5.4b (teker BP'leri) adimina gec")
else:
    print("SONUC : FAIL - plugin yuklenmemis; editoru yeniden baslattigini dogrula, ciktiyi yapistir")
