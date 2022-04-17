import schemathesis
from hypothesis import settings
from schemathesis import from_asgi

from backlog.main import app

# https://schemathesis.readthedocs.io/en/stable/compatibility.html#fastapi
# will install all available compatibility fixups.
schemathesis.fixups.install()

schema = from_asgi("/openapi.json", app)


@schema.parametrize()
def test_no_server_errors(case):
    response = case.call_asgi()
    case.validate_response(response)