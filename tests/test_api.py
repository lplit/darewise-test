import schemathesis
from hypothesis import settings
from schemathesis import from_asgi

from backlog.main import app

# https://schemathesis.readthedocs.io/en/stable/compatibility.html#fastapi
# will install all available compatibility fixups.
schemathesis.fixups.install()

schema = from_asgi("/openapi.json", app)


@schema.parametrize()
@settings(deadline=None, max_examples=1024)
def test_no_server_errors(case):
    case.call_and_validate()
