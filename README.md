# AI-Human TDOA Sound Localization Project

نظام بحثي لتقدير فرق الوصول الزمني (TDOA) وتحديد اتجاه المصدر الصوتي باستخدام أربعة ميكروفونات وشريط مغناطيسي مغلق الحلقة.

## نظرة عامة

يهدف هذا المشروع إلى تصميم وبناء نظام تموضع صوتي تناظري يعتمد على مبدأ **الطاقة المتبقية (Residual Energy)** لتقدير TDOA بين الإشارات المسجلة على شريط مغناطيسي رباعي المسارات. النظام مسجل رقميًا في Python، وموثق بالكامل على مستوى التصميم التكاملي، لكن العتاد الفعلي رباعي الميكروفونات لم يُبن بعد.

### المبدأ التقني

عندما تُسجل إشارتان صوتيتان على شريط مغناطيسي ثم تُقرآن، يمكن إيجاد التأخير الزمني بينهما بطرح إحداهما من الأخرى بعد إزاحة زمنية متغيرة، ثم تربيع الناتج وتكامله. التأخير الذي ينتج عنه أدنى طاقة متبقية هو تقدير TDOA. هذا المبدأ موثق في `integrated_design/analog_processing.md` ومُتحقق منه بالمحاكاة في `src/residual_energy.py` و `src/analog_simulation.py`.

## حالة المشروع الحالية

| المكوّن | الحالة |
|---|---|
| المحاكاة الرقمية (Python) | مكتملة ومُتحقق منها |
| التصميم التكاملي الرباعي | موثق بالكامل (blueprint) |
| العتاد ثنائي القناة | مخطط وموثق، غير مُنفذ بعد |
| العتاد رباعي القنوات | غير مُنفذ |
| البرمجيات المضمنة (Arduino) | نسخة أولية (تحكم بالإطارات) |
| الاختبارات | مكتوبة للمحاكاة |

## بنية المستودع

```text
ai_human_tdoa_project/
├── src/                    # شيفرة Python للمحاكاة والخوارزمية
│   ├── analog_channel_model.py
│   ├── analog_signal_model.py
│   ├── analog_simulation.py
│   ├── residual_energy.py
│   ├── robustness_sweep.py
│   ├── metrics.py
│   ├── plot_results.py
│   └── hardware_config.py
├── firmware/               # شيفرة Arduino للتحكم بالإطارات
│   └── frame_controller.ino
├── hardware/               # المخططات وقائمة القطع
│   ├── block_diagram.md
│   ├── two_channel_schematic.md
│   ├── bill_of_materials.csv
│   └── calibration_procedure.md
├── integrated_design/      # التصميم التكاملي الرباعي
│   ├── README.md
│   ├── four_microphone_geometry.md
│   ├── four_track_tape_format.md
│   ├── analog_processing.md
│   ├── localization_model.md
│   ├── calibration_plan.md
│   └── accuracy_budget.md
├── tests/                  # اختبارات Python
├── results/                # نتائج المحاكاة والرسوم
├── docs/                   # وثائق إضافية
├── pyproject.toml
├── requirements.txt
├── project_vision.md
├── collaboration.md
└── LICENSE.txt
```

## التثبيت

```bash
git clone https://github.com/walidddhony-rgb/ai_human_tdoa_project.git
cd ai_human_tdoa_project
pip install -e ".[dev]"
```

## التشغيل

### تشغيل المحاكاة الأساسية

```bash
python -m src.analog_simulation
```

### تشغيل اختبار المتانة (Robustness Sweep)

```bash
python -m src.robustness_sweep
```

### تشغيل الاختبارات

```bash
pytest tests/
```

## الأهداف التقنية

- إثبات مبدأ الطاقة المتبقية لتقدير TDOA على شريط مغناطيسي حقيقي
- بناء نموذج أولي ثنائي القناة كإثبات مفهوم
- التوسع إلى نظام رباعي الميكروفونات لتحديد الاتجاه
- تحقيق دقة TDOA ≤ 50 µs وخطأ زاوي ≤ 5°

## الترخيص

هذا المشروع مرخص تحت **Humanitarian & Ethical Use License (HEUL)** — راجع `LICENSE.txt` للتفاصيل.

## المساهمة

راجع `collaboration.md` لفهم نموذج التعاون والفريق.
