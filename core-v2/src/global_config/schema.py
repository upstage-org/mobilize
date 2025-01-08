import os
import sys

# Always on top
app_dir = os.path.abspath(os.path.dirname(__file__))
prodder = os.path.abspath(os.path.join(app_dir, ".."))
sys.path.append(app_dir)
sys.path.append(prodder)
from ariadne import MutationType, QueryType, make_executable_schema
from fastapi import FastAPI
from ariadne.asgi import GraphQL


def config_graphql_endpoints(app: FastAPI):
    from assets.http.schema import query as asset_query, mutation as asset_mutation
    from studios.http.schema import (
        query as studio_query,
        mutation as studio_mutation,
    )
    from authentication.http.schema import mutation as auth_mutation
    from licenses.http.schema import mutation as license_mutation
    from mails.http.schema import mutation as mail_mutation
    from payments.http.schema import mutation as payment_mutation
    from studios.http.graphql import type_defs as studio_type_defs
    from performance_config.http.schema import query as performance_query
    from stages.http.schema import query as stage_query, mutation as stage_mutation
    from upstage_options.http.schema import (
        query as upstage_options_query,
        mutation as upstage_options_mutation,
    )
    from users.http.schema import query as user_query, mutation as user_mutation

    combined_query = QueryType()
    combined_mutation = MutationType()

    combined_mutation.set_field("login", auth_mutation._resolvers["login"])
    combined_mutation.set_field(
        "refreshToken", auth_mutation._resolvers["refreshToken"]
    )
    combined_mutation.set_field("logout", auth_mutation._resolvers["logout"])

    combined_mutation.set_field(
        "createLicense", license_mutation._resolvers["createLicense"]
    )
    combined_mutation.set_field(
        "revokeLicense", license_mutation._resolvers["revokeLicense"]
    )

    combined_mutation.set_field(
        "sendEmailExternal", mail_mutation._resolvers["sendEmailExternal"]
    )

    combined_mutation.set_field(
        "oneTimePurchase", payment_mutation._resolvers["oneTimePurchase"]
    )
    combined_mutation.set_field(
        "createSubscription", payment_mutation._resolvers["createSubscription"]
    )
    combined_mutation.set_field(
        "cancelSubscription", payment_mutation._resolvers["cancelSubscription"]
    )
    combined_mutation.set_field(
        "updateEmailCustomer", payment_mutation._resolvers["updateEmailCustomer"]
    )

    combined_query.set_field(
        "performanceCommunication",
        performance_query._resolvers["performanceCommunication"],
    )
    combined_query.set_field(
        "performanceConfig", performance_query._resolvers["performanceConfig"]
    )
    combined_query.set_field("scene", performance_query._resolvers["scene"])
    combined_query.set_field("parentStage", performance_query._resolvers["parentStage"])

    combined_query.set_field("stages", stage_query._resolvers["stages"])
    combined_query.set_field("foyerStageList", stage_query._resolvers["foyerStageList"])
    combined_query.set_field("stage", stage_query._resolvers["stage"])
    combined_query.set_field("stageList", stage_query._resolvers["stageList"])

    combined_mutation.set_field("createStage", stage_mutation._resolvers["createStage"])
    combined_mutation.set_field("updateStage", stage_mutation._resolvers["updateStage"])
    combined_mutation.set_field("deleteStage", stage_mutation._resolvers["deleteStage"])
    combined_mutation.set_field("assignMedia", stage_mutation._resolvers["assignMedia"])
    combined_mutation.set_field(
        "duplicateStage", stage_mutation._resolvers["duplicateStage"]
    )
    combined_mutation.set_field("uploadMedia", stage_mutation._resolvers["uploadMedia"])
    combined_mutation.set_field(
        "deleteMediaOnStage", stage_mutation._resolvers["deleteMediaOnStage"]
    )
    combined_mutation.set_field("updateMedia", stage_mutation._resolvers["updateMedia"])
    combined_mutation.set_field(
        "assignStages", stage_mutation._resolvers["assignStages"]
    )
    combined_mutation.set_field("sweepStage", stage_mutation._resolvers["sweepStage"])
    combined_mutation.set_field("saveScene", stage_mutation._resolvers["saveScene"])
    combined_mutation.set_field("deleteScene", stage_mutation._resolvers["deleteScene"])
    combined_mutation.set_field(
        "updatePerformance", stage_mutation._resolvers["updatePerformance"]
    )
    combined_mutation.set_field(
        "deletePerformance", stage_mutation._resolvers["deletePerformance"]
    )
    combined_mutation.set_field(
        "startRecording", stage_mutation._resolvers["startRecording"]
    )
    combined_mutation.set_field(
        "saveRecording", stage_mutation._resolvers["saveRecording"]
    )
    combined_mutation.set_field(
        "updateStatus", stage_mutation._resolvers["updateStatus"]
    )
    combined_mutation.set_field(
        "updateVisibility", stage_mutation._resolvers["updateVisibility"]
    )
    combined_mutation.set_field(
        "updateLastAccess", stage_mutation._resolvers["updateLastAccess"]
    )

    combined_query.set_field("currentUser", user_query._resolvers["currentUser"])
    combined_mutation.set_field("createUser", user_mutation._resolvers["createUser"])
    combined_mutation.set_field(
        "requestPasswordReset", user_mutation._resolvers["requestPasswordReset"]
    )
    combined_mutation.set_field(
        "verifyPasswordReset", user_mutation._resolvers["verifyPasswordReset"]
    )
    combined_mutation.set_field(
        "resetPassword", user_mutation._resolvers["resetPassword"]
    )

    combined_query.set_field("nginx", upstage_options_query._resolvers["nginx"])
    combined_query.set_field("system", upstage_options_query._resolvers["system"])
    combined_query.set_field("foyer", upstage_options_query._resolvers["foyer"])

    combined_mutation.set_field(
        "updateTermsOfService",
        upstage_options_mutation._resolvers["updateTermsOfService"],
    )
    combined_mutation.set_field(
        "saveConfig", upstage_options_mutation._resolvers["saveConfig"]
    )
    combined_mutation.set_field(
        "sendSystemEmail", upstage_options_mutation._resolvers["sendSystemEmail"]
    )

    combined_query.set_field("media", asset_query._resolvers["media"])
    combined_query.set_field("whoami", studio_query._resolvers["whoami"])
    combined_query.set_field("adminPlayers", studio_query._resolvers["adminPlayers"])
    combined_query.set_field("users", studio_query._resolvers["users"])
    combined_query.set_field("getAllStages", studio_query._resolvers["getAllStages"])
    combined_query.set_field("mediaList", asset_query._resolvers["mediaList"])
    combined_query.set_field("tags", asset_query._resolvers["tags"])
    combined_query.set_field("mediaTypes", asset_query._resolvers["mediaTypes"])
    combined_query.set_field("voices", asset_query._resolvers["voices"])

    combined_mutation.set_field(
        "batchUserCreation", studio_mutation._resolvers["batchUserCreation"]
    )
    combined_mutation.set_field("uploadFile", asset_mutation._resolvers["uploadFile"])
    combined_mutation.set_field("saveMedia", asset_mutation._resolvers["saveMedia"])
    combined_mutation.set_field("deleteMedia", asset_mutation._resolvers["deleteMedia"])
    combined_mutation.set_field("updateUser", studio_mutation._resolvers["updateUser"])
    combined_mutation.set_field("deleteUser", studio_mutation._resolvers["deleteUser"])
    combined_mutation.set_field("sendEmail", studio_mutation._resolvers["sendEmail"])
    combined_mutation.set_field(
        "changePassword", studio_mutation._resolvers["changePassword"]
    )
    combined_mutation.set_field("calcSizes", studio_mutation._resolvers["calcSizes"])
    combined_mutation.set_field(
        "requestPermission",
        studio_mutation._resolvers["requestPermission"],
    )
    combined_mutation.set_field(
        "confirmPermission",
        studio_mutation._resolvers["confirmPermission"],
    )
    combined_mutation.set_field(
        "quickAssignMutation",
        studio_mutation._resolvers["quickAssignMutation"],
    )
    combined_schema = make_executable_schema(
        studio_type_defs, combined_query, combined_mutation
    )

    combined_graphql_app = GraphQL(combined_schema, debug=True)

    app.add_route("/api/studio_graphql", combined_graphql_app)
    app.add_websocket_route("/api/studio_graphql", combined_graphql_app)
