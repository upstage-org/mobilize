from ariadne import MutationType, QueryType, make_executable_schema
from ariadne.asgi import GraphQL
from authentication.http.validation import LoginInput
from authentication.services.auth import AuthenticationService
from studios.http.graphql import type_defs


query = QueryType()
mutation = MutationType()


@mutation.field("login")
async def login(
    _,
    info,
    payload: LoginInput,
    authentication_service: AuthenticationService = AuthenticationService(),
):
    return await authentication_service.login(
        LoginInput(**payload), info.context["request"]
    )


@mutation.field("refreshToken")
async def refresh_token(_, info):
    return await AuthenticationService().refresh_token(
        info.context["request"],
    )


@mutation.field("logout")
async def resolve_logout(
    _,
    info,
    authentication_service: AuthenticationService = AuthenticationService(),
):
    return await authentication_service.logout(info.context["request"])


schema = make_executable_schema(type_defs, query, mutation)
auth_graphql_app = GraphQL(schema, debug=True)
