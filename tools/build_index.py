"""Validates every question set in sets/ and rebuilds index.json (run by GitHub Actions on every upload)."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETS = os.path.join(ROOT, "sets")
errors, refs, ids = [], [], set()

for name in sorted(os.listdir(SETS)) if os.path.isdir(SETS) else []:
    if not name.lower().endswith(".json"):
        continue
    path = os.path.join(SETS, name)
    try:
        with open(path, encoding="utf-8-sig") as f:
            s = json.load(f)
    except Exception as e:
        errors.append(f"{name}: فایل JSON معتبر نیست ({e})"); continue
    sid = s.get("id")
    qs = s.get("questions")
    if not sid or not isinstance(qs, list) or not qs:
        errors.append(f"{name}: شناسه (id) یا فهرست سؤال‌ها (questions) ندارد"); continue
    if sid in ids:
        errors.append(f"{name}: شناسهٔ «{sid}» تکراری است"); continue
    bad = []
    for i, q in enumerate(qs, 1):
        opts = q.get("options") or []
        n = len(opts) or q.get("optionCount", 4)
        if not q.get("id") or not (q.get("text") or q.get("image")) or not isinstance(q.get("answer"), int) or not 1 <= q["answer"] <= n:
            bad.append(str(i))
    if bad:
        errors.append(f"{name}: سؤال‌های شمارهٔ {', '.join(bad[:10])} ناقص‌اند (متن، گزینه یا پاسخ درست)"); continue
    ids.add(sid)
    refs.append({"id": sid, "file": f"sets/{name}", "title": s.get("title", sid), "description": s.get("description", ""), "questions": len(qs)})

if errors:
    print("\n".join("❌ " + e for e in errors))
    sys.exit(1)

with open(os.path.join(ROOT, "index.json"), "w", encoding="utf-8") as f:
    json.dump({"version": 2, "sets": refs}, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(f"✅ {len(refs)} مجموعه، {sum(r['questions'] for r in refs)} سؤال")
