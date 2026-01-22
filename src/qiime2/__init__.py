# ----------------------------------------------------------------------------
# Copyright (c) 2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib
import sys

rachis = importlib.import_module("rachis")
sys.modules[__name__] = rachis

qiime2_path = __name__ + "."
rachis_path = rachis.__name__ + "."

# Duplicate anything already loaded from rachis as also from qiime2 so that
# the modules are not executed again as the path is followed
# This avoids allocation and new id() which break isinstance checks across
# the namespaces
for name, module in list(sys.modules.items()):
    if name.startswith(rachis_path):
        sys.modules[qiime2_path + name[len(rachis_path):]] = module
