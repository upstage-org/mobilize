// @ts-nocheck
import { GraphQLClient } from "graphql-request";
export { gql } from "graphql-request";
import config from "config";
import store from "store/index";

export const createClient = (namespace: any) => ({
  request: async (...params: any) => {
    let response = null;
    const options = {
      headers: {},
    };
    const client = new GraphQLClient(
      `${config.GRAPHQL_ENDPOINT}${namespace}`,
      options,
    );
    const token = store.getters["auth/getToken"];
    if (token) {
      client.setHeader("Authorization", `Bearer ${token}`);
    }
    try {
      response = await client.request(...params);
    } catch (error: any) {
      const isRefresh = error.request.query
        .trim()
        .startsWith("mutation RefreshToken");
      const refreshToken = store.getters["auth/getRefreshToken"];
      if (
        !isRefresh &&
        refreshToken &&
        error.response.errors[0].message === "Signature has expired"
      ) {
        const newToken = await store.dispatch("auth/fetchRefreshToken");
        client.setHeader("Authorization", `Bearer ${newToken}`);
        response = await client.request(...params);
      } else {
        throw error;
      }
    }
    return response;
  },
});
