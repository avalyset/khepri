"""Put `src/` on the import path for the whole suite.

Before this file, `test_ci.py` and `test_forecast.py` each did the
`sys.path.insert` themselves at import time. That worked for the full run only
because pytest collects alphabetically and those two sort first: by the time
`test_codecarbon_delivery.py` or `test_peat_guard.py` was imported, `src/` was
already on the path. Running either of those files on its own failed with
`ModuleNotFoundError: No module named 'khepri'`.

conftest.py is imported before any test module in the directory, so the path is
set once, for every file, however the suite is invoked.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
