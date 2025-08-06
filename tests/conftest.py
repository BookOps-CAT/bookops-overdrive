import json
import os

import pytest


@pytest.fixture
def live_creds() -> None:
    with open(
        os.path.join(
            os.environ["USERPROFILE"], ".cred/.overdrive/overdrive_creds.json"
        ),
        "r",
    ) as fh:
        creds = json.load(fh)
        for k, v in creds.items():
            os.environ[k] = v
