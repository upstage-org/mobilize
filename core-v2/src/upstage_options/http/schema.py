from ariadne import MutationType, QueryType, make_executable_schema

from global_config import authenticated
from upstage_options.http.validation import ConfigInput, SystemEmailInput
from upstage_options.services.upstage_option import SettingService
from studios.http.graphql import type_defs
from ariadne.asgi import GraphQL

from users.db_models.user import ADMIN, SUPER_ADMIN

query = QueryType()
mutation = MutationType()


@query.field("nginx")
def nginx(*_):
    return SettingService().upload_limit()


@query.field("system")
def system(*_):
    return SettingService().system_info()


@query.field("foyer")
def foyer(*_):
    return SettingService().foyer_info()


@mutation.field("updateTermsOfService")
@authenticated(allowed_roles=[ADMIN, SUPER_ADMIN])
def update_terms_of_service(*_, url: str):
    return SettingService().update_terms_of_service(url)


@mutation.field("saveConfig")
@authenticated(allowed_roles=[ADMIN, SUPER_ADMIN])
async def save_config(*_, input: ConfigInput):
    return SettingService().save_config(ConfigInput(**input))


@mutation.field("sendSystemEmail")
@authenticated(allowed_roles=[ADMIN, SUPER_ADMIN])
async def send_email(*_, input: SystemEmailInput):
    return await SettingService().send_email(SystemEmailInput(**input))


schema = make_executable_schema(type_defs, query, mutation)
config_graphql_app = GraphQL(schema, debug=True)
