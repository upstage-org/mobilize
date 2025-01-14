// @ts-nocheck
import { gql } from "graphql-request";
import { createClient } from "./graphql";
import { studioClient } from './';
import _ from 'lodash';

export const userFragment = gql`
  fragment userFragment on User {
    id
    username
    firstName
    lastName
    displayName
    email
    active
    createdOn
    role
    uploadLimit
    intro
  }
`;

export default {
  login: (variables) =>
    studioClient.request(
      gql`
        mutation login(
          $username: String!
          $password: String!
        ) {
          login(payload: {
              username: $username
              password: $password
          }) {
              user_id
              access_token
              refresh_token
              role
              first_name
              groups {
                  id
                  name
              }
              username
              title
          }
        }
      `,
      variables,
    ),
  refreshUser: (variables, headers) =>
    studioClient.request(
      gql`
          mutation {
              refreshToken {
                  access_token
                  refresh_token
              }
          }
        `,
      variables,
      headers,
    ),
  currentUser: () =>
    studioClient.request(gql`
        query {
            currentUser {
                id
                username
                firstName
                lastName
                displayName
                email
                active
                createdOn
                role
                uploadLimit
                intro
            }
        }
      `),

  createUser: (variables) =>
    studioClient.request(
      gql`
        mutation CreateUser(
          $username: String!
          $password: String!
          $email: String
          $firstName: String
          $lastName: String
          $intro: String
          $token: String
        ) {
          createUser(
            inbound: {
              username: $username
              password: $password
              email: $email
              firstName: $firstName
              lastName: $lastName
              intro: $intro
              token: $token
            }
          ) {
            user {
              ...userFragment
            }
          }
        }
        ${userFragment}
      `,
      variables,
    ),
  updateUser: (variables) =>
    studioClient.request(
      gql`
        mutation UpdateUser(
          $id: ID!
          $username: String!
          $displayName: String
          $firstName: String
          $lastName: String
          $email: String
          $password: String
          $active: Boolean
          $role: Int
          $uploadLimit: Int
          $intro: String
          $binName: String
        ) {
          updateUser(
            input: {
              id: $id
              username: $username
              displayName: $displayName
              firstName: $firstName
              lastName: $lastName
              email: $email
              password: $password
              active: $active
              role: $role
              uploadLimit: $uploadLimit
              intro: $intro
              binName: $binName
            }
          ) {
            ...userFragment
          }
        }
        ${userFragment}
      `,
      {
        ..._.omitBy(variables, _.isNil),
        ...variables.role ? { role: parseInt(variables.role) } : {},
        binName: ""
      },
    ),

  userList: () =>
    studioClient.request(gql`
      query UserList {
        users(active: true) {
            ...userFragment
        }
      }
      ${userFragment}
    `),

  changePassword: (variables) =>
    studioClient.request(
      gql`
        mutation ChangePassword(
          $id: ID!
          $oldPassword: String!
          $newPassword: String!
        ) {
          changePassword(
            input: {
              id: $id
              oldPassword: $oldPassword
              newPassword: $newPassword
            }
          ) {
            success
            message
          }
        }
      `,
      variables,
    ),
  requestPasswordReset: (variables) =>
    studioClient.request(
      gql`
        mutation RequestPasswordReset($usernameOrEmail: String!) {
          requestPasswordReset(email: $usernameOrEmail) {
            message
          }
        }
      `,
      variables,
    ),
  verifyPasswordReset: (variables) =>
    studioClient.request(
      gql`
        mutation verifyPasswordReset($username: String, $otp: String) {
          verifyPasswordReset(username: $username, otp: $otp) {
            message
          }
        }
      `,
      variables,
    ),
  passwordReset: (variables) =>
    studioClient.request(
      gql`
        mutation PasswordReset(
          $username: String
          $otp: String
          $password: String
        ) {
          passwordReset(username: $username, otp: $otp, password: $password) {
            message
          }
        }
      `,
      variables,
    ),
  adminPlayers: () =>
    studioClient.request(gql`
        query adminPlayers {
          adminPlayers {
              edges {
                id
                username
                email
                role
                firstName
                lastName
                displayName
              }
          }
        }
      `),
};
