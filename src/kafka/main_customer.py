import sys
from pathlib import Path
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
file = Path(__file__).resolve()
root = file.parents[2]
sys.path.append(str(Path(root).joinpath("src/server")))
sys.path.append(str(root))

import django
django.setup()

from wineup.models import Wine, User, Review

print(User.objects.all())
