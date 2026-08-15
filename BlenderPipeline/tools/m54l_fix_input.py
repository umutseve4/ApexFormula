# m54l_fix_input.py v2 - M5.4f deneme #5 devam: Enhanced Input onarimi
# v1 SONUCU: FIND 4/4 PASS, VALTYPE 3/3 PASS, INI PASS;
#   IMC_MAPPINGS FAIL -> TypeError: unreal.Key(key_name=...) ctor arguman almiyor (UE 5.8 API gap #6)
#   AYRICA v1 kesfi: IMC icinde 4 esleme ZATEN VAR (action'lar dogru sirada:
#   Throttle/Brake/Steer/Steer) ama key alanlari bos/gecersiz gorunuyor.
# v2 STRATEJI: yeni esleme insa ETME; MEVCUT 4 eslemenin key'ini yerinde doldur:
#   [0]=W(Throttle) [1]=S(Brake) [2]=D(Steer) [3]=A(Steer, Negate modifier).
#   Key kurulumu 2 kademeli dener: set_editor_property("key_name") -> attr atama.
# Play GEREKMEZ. PASS sonrasi UE YENIDEN BASLATILMALI (ini acilista okunur).
import unreal

TAG = "[M54L]"
def log(m): unreal.log(TAG + " " + m)

results = []
def check(name, ok, detail):
    results.append((name, bool(ok), detail))
    log("%s %s  %s" % (name, "PASS" if ok else "FAIL", detail))

IMC_PATH = "/Game/vehicle/IMC_AF_Drive"   # v1 AssetRegistry ile dogrulandi
eal = unreal.EditorAssetLibrary
imc = eal.load_asset(IMC_PATH)
check("LOAD_IMC", imc is not None, IMC_PATH)

def make_key(kn):
    k = unreal.Key()
    try:
        k.set_editor_property("key_name", kn)
        return k, "set_editor_property"
    except Exception:
        pass
    try:
        k.key_name = kn
        return k, "attr"
    except Exception as e:
        raise RuntimeError("Key kurulamadi (%s): %r" % (kn, e))

if imc:
    maps = list(imc.get_editor_property("mappings"))
    check("MAP_COUNT", len(maps) == 4, "n=%d (4 beklenir)" % len(maps))

    desired = [("IA_Throttle", "W", False),
               ("IA_Brake",    "S", False),
               ("IA_Steer",    "D", False),
               ("IA_Steer",    "A", True)]

    if len(maps) == 4:
        try:
            for i, (m, (act_name, kn, neg)) in enumerate(zip(maps, desired)):
                act = m.get_editor_property("action")
                real = act.get_name() if act else "None"
                old_key = ""
                try:
                    old_key = str(m.get_editor_property("key").get_editor_property("key_name"))
                except Exception:
                    old_key = "?"
                if real != act_name:
                    check("ORDER_%d" % i, False, "beklenen=%s gercek=%s" % (act_name, real))
                    continue
                k, yol = make_key(kn)
                m.set_editor_property("key", k)
                if neg:
                    neg_obj = unreal.new_object(unreal.InputModifierNegate, outer=imc)
                    m.set_editor_property("modifiers", [neg_obj])
                log("map[%d] %s: key %s -> %s (%s%s)" %
                    (i, real, old_key, kn, yol, " +Negate" if neg else ""))

            imc.set_editor_property("mappings", maps)
            saved = eal.save_loaded_asset(imc)

            # read-back dogrulama
            back = imc.get_editor_property("mappings")
            got = []
            for m in back:
                a = m.get_editor_property("action")
                kn2 = str(m.get_editor_property("key").get_editor_property("key_name"))
                nmod = len(m.get_editor_property("modifiers"))
                got.append("%s=%s(mod:%d)" % (a.get_name() if a else "None", kn2, nmod))
            expect = ["IA_Throttle=W(mod:0)", "IA_Brake=S(mod:0)",
                      "IA_Steer=D(mod:0)", "IA_Steer=A(mod:1)"]
            ok = saved and got == expect
            check("IMC_KEYS", ok, "; ".join(got))
        except Exception as e:
            check("IMC_KEYS", False, repr(e))

# ---------- OTOMATIK KONTROL ----------
log("===== OTOMATIK KONTROL =====")
allok = all(ok for _, ok, _ in results) and len(results) >= 3
for name, ok, detail in results:
    log("%-10s: %s  (%s)" % (name, "PASS" if ok else "FAIL", detail))
log("SONUC %s" % ("PASS - UE'yi TAMAMEN KAPAT/AC, sonra m54k'yi tekrar kostur" if allok
                  else "FAIL - ciktiyi raporla"))
