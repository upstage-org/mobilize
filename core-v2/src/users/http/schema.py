from ariadne import MutationType, QueryType, make_executable_schema
from global_config import convert_keys_to_camel_case, authenticated
from studios.http.graphql import type_defs
from ariadne.asgi import GraphQL

from users.http.validation import CreateUserInput
from users.services.user import UserService

query = QueryType()
mutation = MutationType()


@query.field("currentUser")
@authenticated()
def current_user(_, info):
    return convert_keys_to_camel_case(info.context["request"].state.current_user)


@mutation.field("createUser")
def create_user(_, info, inbound: CreateUserInput, user_service=UserService()):
    return user_service.create(inbound, info.context["request"])


@mutation.field("requestPasswordReset")
async def request_password_reset(_, info, email, user_service=UserService()):
    return await user_service.request_password_reset(email)


@mutation.field("verifyPasswordReset")
async def verify_password_reset(_, info, input, user_service=UserService()):
    return await user_service.verify_password_reset(input)


@mutation.field("resetPassword")
async def reset_password(_, info, input, user_service=UserService()):
    return await user_service.reset_password(input)


schema = make_executable_schema(type_defs, query, mutation)
user_graphql_app = GraphQL(schema, debug=True)
