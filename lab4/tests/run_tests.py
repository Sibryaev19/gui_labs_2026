import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import test_backend

failures = 0
for name in sorted(dir(test_backend)):
    if not name.startswith("test_"):
        continue
    fn = getattr(test_backend, name)
    try:
        fn()
        print("OK   " + name)
    except Exception:
        failures += 1
        print("FAIL " + name)
        traceback.print_exc()

print()
if failures:
    print("Провалено тестов:", failures)
    sys.exit(1)
print("Все тесты прошли")
