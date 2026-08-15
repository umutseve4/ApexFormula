# m54n_register_imc.py - M5.4f deneme #7: IMC'yi motora KALICI kaydet
# Yol 1: EnhancedInputDeveloperSettings CDO'suna default_mapping_contexts ekle (bu oturumda etkili)
# Yol 2: DefaultInput.ini'de satirin DOGRU section altinda olmasini garanti et (kalici)
# Play GEREKMEZ. Calistir -> sonra Play + W dene.
import unreal, os

R = []
def log(tag, ok, info=""):
    s = "PASS" if ok else "FAIL"
    unreal.log("[M54N] " + tag + " " + s + "  " + str(info))
    R.append((tag, ok, str(info)))

IMC_PATH = "/Game/vehicle/IMC_AF_Drive"
imc = unreal.load_asset(IMC_PATH)
log("IMC_LOAD", imc is not None, IMC_PATH)

# ---- Yol 1: CDO ----
settings = None
try:
    settings = unreal.get_default_object(unreal.EnhancedInputDeveloperSettings)
    log("CDO", True, settings.get_name())
except Exception as e:
    log("CDO", False, e)

if settings and imc:
    try:
        arr = settings.get_editor_property("default_mapping_contexts")
        before = len(arr)
        already = False
        for m in arr:
            try:
                if "IMC_AF_Drive" in str(m.get_editor_property("input_mapping_context")):
                    already = True
            except Exception:
                pass
        if not already:
            entry = None
            for cls_name in ("DefaultMappingContextSetting",):
                try:
                    entry = getattr(unreal, cls_name)()
                    break
                except Exception:
                    entry = None
            if entry is None:
                log("ENTRY_CTOR", False, "DefaultMappingContextSetting yok")
            else:
                try:
                    entry.set_editor_property("input_mapping_context", imc)
                except Exception as e:
                    log("ENTRY_SET_IMC", False, e)
                try:
                    entry.set_editor_property("priority", 0)
                except Exception:
                    pass
                arr.append(entry)
                settings.set_editor_property("default_mapping_contexts", arr)
        arr2 = settings.get_editor_property("default_mapping_contexts")
        found = False
        for m in arr2:
            try:
                if "IMC_AF_Drive" in str(m.get_editor_property("input_mapping_context")):
                    found = True
            except Exception:
                pass
        log("CDO_REGISTER", found, "count " + str(before) + " -> " + str(len(arr2)))
    except Exception as e:
        log("CDO_REGISTER", False, e)

# ---- Yol 2: INI section onarimi ----
GOOD_SECTION = "[/Script/EnhancedInput.EnhancedInputDeveloperSettings]"
LINE = '+DefaultMappingContexts=(InputMappingContext="/Game/vehicle/IMC_AF_Drive.IMC_AF_Drive",Priority=0)'
try:
    cfg = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_config_dir())
    ini = os.path.join(cfg, "DefaultInput.ini")
    with open(ini, "r", encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f.readlines()]
    # satir hangi section altinda?
    cur_sec = ""
    line_sec = None
    good_idx = None
    for i, l in enumerate(lines):
        ls = l.strip()
        if ls.startswith("["):
            cur_sec = ls
        if ls == GOOD_SECTION:
            good_idx = i
        if "IMC_AF_Drive" in ls and "DefaultMappingContexts" in ls:
            line_sec = cur_sec
    log("INI_SCAN", True, "satirin sectioni: " + str(line_sec))
    changed = False
    if line_sec != GOOD_SECTION:
        # yanlis/eksik: dogru section altina ekle
        if good_idx is None:
            lines.append("")
            lines.append(GOOD_SECTION)
            lines.append(LINE)
        else:
            lines.insert(good_idx + 1, LINE)
        changed = True
    if changed:
        with open(ini, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
    # dogrulama: tekrar oku
    with open(ini, "r", encoding="utf-8") as f:
        txt = f.read()
    ok = False
    sec_pos = txt.find(GOOD_SECTION)
    if sec_pos >= 0:
        nxt = txt.find("[", sec_pos + 1)
        chunk = txt[sec_pos: nxt if nxt > 0 else len(txt)]
        ok = "IMC_AF_Drive" in chunk
    log("INI_FIX", ok, "dogru section altinda" if ok else "hala yanlis")
except Exception as e:
    log("INI_FIX", False, e)

unreal.log("[M54N] ===== OTOMATIK KONTROL =====")
fails = []
for tag, ok, info in R:
    unreal.log("[M54N] " + tag.ljust(14) + ": " + ("PASS" if ok else "FAIL") + "  (" + info + ")")
    if not ok:
        fails.append(tag)
if fails:
    unreal.log("[M54N] SONUC FAIL: " + ",".join(fails))
else:
    unreal.log("[M54N] SONUC PASS - simdi Play'e bas, viewport'a tikla, W dene")
