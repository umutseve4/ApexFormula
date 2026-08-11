# CI Marker -- Wave 2 Verification Batch 1

Bu dosya yalnızca CI kanıtı üretmek için vardır. Hiçbir üretim kodu veya
konfigürasyon içermez ve `main` dalına birleştirilmez.

## Amaç

`main` dalına doğrudan atılan aşağıdaki commit'ler, kendi başlarına hiçbir
pull request diff'inde görünmediği için check-run kaydı üretmemiştir. Bu
marker commit'i ile açılan taslak PR, o commit'leri diff kapsamına alır ve
CI'nin bunları gerçekten yeşil değerlendirdiğini kanıtlar.

| # | Dosya | Commit | Nitelik |
|---|---|---|---|
| 18 | `Documentation/CI_EVIDENCE_VOL2.md` | `2267c6de` | belge |
| 19 | `Documentation/DECISION_LOG_VOL3.md` | `bb9a83e2` | belge (D-051) |
| 20 | `Tools/af_validate_interfaces.py` | `f1cea387` | **kod** (dalga 1.5 #2) |
| 21 | `BlenderPipeline/scripts/af_pipeline_config.py` | `86d74ecc` | **kod** (dalga 1.5 #1) |
| 22 | `Tools/af_config_hash_guard.py` | `aa5283c7` | **kod** (dalga 1.5 #3) |

## Kanıt kriteri

Kabul yalnızca şu iki koşul birlikte sağlanırsa verilir:

1. On işin (10/10) tamamı `conclusion == "success"`.
2. Her işin `started_at` değeri bu marker commit'inin yazar tarihinden
   **sonra** olmalıdır. Aksi hâlde okunan sonuç bayattır.

9/10 bir geçiş değildir; Blender işi `in_progress` iken okuma tekrarlanır.

## Bu turda özel olarak sınanan şey

`86d74ecc` commit'i `BlenderPipeline/scripts/af_pipeline_config.py`
içindeki `PROJECT_NAME` değerini `UludagFormula` yapar. D-051 F-2 bulgusu,
`PROJECT_NAME` alanının `effective_config()` sözlüğünün üyesi olmadığını ve
bu nedenle D-046 ile sabitlenen konfigürasyon karmasının **değişemeyeceğini**
öne sürer. Bu bulgu şu ana kadar yalnızca kaynak okunarak doğrulanmıştır.

Bu partinin yeşil geçmesi, `af_config_hash_guard.py` denetimi A'nın sabitlenmiş
karmayı hâlâ eşleştirdiği anlamına gelir ve F-2'yi *okuyarak doğrulanmış*
durumundan *çalıştırılarak doğrulanmış* durumuna yükseltir. Kırmızı geçmesi,
yeniden sabitleme (re-pin) gerektiğini kanıtlar.

## Durum

Bu marker, sonucu `Documentation/CI_EVIDENCE_VOL2.md` dosyasına işlendikten
sonra ilgili PR kapatılarak (birleştirilmeden) terk edilir.
