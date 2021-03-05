import { GraphQLClient } from 'graphql-request';
export { gql } from 'graphql-request';
import config from '@/config';
import store from "@/store/index";


const options = { headers: {} };

export const createClient = namespace => ({
    request: async (...params) => {
        const client = new GraphQLClient(`${config.GRAPHQL_ENDPOINT}${namespace}/`, options)
        const token = store.getters["auth/getToken"] || "";
        if (token) {
            client.setHeader('X-Access-Token', token)
        }
        try {
            const response = await client.request(...params);
            return response;
        } catch (error) {
            const refreshToken = store.getters["auth/getRefreshToken"]
            if (refreshToken) {
                if (error.response.errors[0].message === 'Signature has expired') { // refresh token
                    const newToken = await store.dispatch("auth/fetchRefreshToken");
                    client.setHeader('X-Access-Token', newToken);
                    return client.request(...params);
                }
            }
            throw (error);
        }

    }
})