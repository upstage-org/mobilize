from ariadne import MutationType, QueryType, make_executable_schema
from studios.http.graphql import type_defs
from ariadne.asgi import GraphQL
from licenses.http.validation import LicenseInput
from licenses.services.license import LicenseService

mutation = MutationType()
query = QueryType()


@mutation.field("createLicense")
def create_license(_, __, input):
    return LicenseService().create_license(LicenseInput(**input))


@mutation.field("revokeLicense")
def revoke_license(_, __, id: int):
    return LicenseService().revoke_license(id)


schema = make_executable_schema(type_defs, query, mutation)
license_graphql_app = GraphQL(schema, debug=True)
