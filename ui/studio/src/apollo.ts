import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client/core'
import configs from './config'

// HTTP connection to the API
const httpLink = createHttpLink({
  // You should use an absolute URL here
  uri: configs.GRAPHQL_ENDPOINT,
})

// Cache implementation
const cache = new InMemoryCache()

// Create the apollo client
export const apolloClient = new ApolloClient({
  link: httpLink,
  cache,
})