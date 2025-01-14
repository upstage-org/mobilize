// @ts-nocheck
import { gql } from "graphql-request";
import { stageGraph, studioClient } from ".";
import { studioClient } from '../graphql';

export const stageFragment = gql`
  fragment stageFragment on Stage {
    id
    name
    fileLocation
    status
    visibility
    cover
    description
    playerAccess
    permission
    lastAccess
    owner {
      id
      username
      displayName
    }
  }
`;

export const assetFragment = gql`
  fragment assetFragment on Asset {
    id
    name
    src
    sign
    createdOn
    size
    description
    assetType {
      id
      name
    }
    owner {
      id
      username
      displayName
    }
    copyrightLevel
    permissions {
      id
      userId
      assetId
      approved
      seen
      note
      user {
        username
      }
    }
  }
`;

export const sceneFragment = gql`
  fragment sceneFragment on Scene {
    id
    name
    
  }
`;

export default {
  createStage: async (variables) => {
    let result = await studioClient.request(
      gql`
        mutation CreateStage($name: String, $fileLocation: String) {
          createStage(input: { name: $name, fileLocation: $fileLocation }) {
            stage {
              id
            }
          }
        }
      `,
      variables,
    );
    if (result) {
      variables.id = result.createStage.stage.id;
      result = await stageGraph.updateStage(variables);
      return result.updateStage.stage;
    }
  },
  updateStage: (variables) =>
    studioClient.request(
      gql`
        mutation UpdateStage(
          $id: ID!
          $name: String
          $description: String
          $fileLocation: String
          $status: String
          $visibility: Boolean
          $cover: String
          $playerAccess: String
        ) {
          updateStage(
            input: {
              id: $id
              name: $name
              description: $description
              fileLocation: $fileLocation
              status: $status
              visibility: $visibility
              cover: $cover
              playerAccess: $playerAccess
            }
          ) {
            ...stageFragment
          }
        }
        ${stageFragment}
      `,
      variables,
    ),
  updateStatus: (stageId) =>
    studioClient.request(gql`
  mutation {
    updateStatus(id: "${stageId}" ) {
      result
    }
  }
  `),
  updateVisibility: (stageId) =>
    studioClient.request(gql`
  mutation {
    updateVisibility(id: "${stageId}" ) {
      result
    }
  }
  `),
  updateLastAccess: (stageId) =>
    studioClient.request(gql`
  mutation {
    updateLastAccess(stageId: "${stageId}" ) {
      result
    }
  }
  `),
  sweepStage: (variables) =>
    studioClient.request(
      gql`
        mutation SweepStage($id: ID!) {
          sweepStage(id: $id) {
              success
              performanceId
          }
        }
      `,
      variables,
    ),
  stageList: (variables) =>
    studioClient.request(
      gql`
        query StageTable(
          $page: Int
          $limit: Int
        ) {
          stages(input:{
            page: $page
            limit: $limit
          }) {
            totalCount
            edges {
                ...stageFragment
            }
          }
        }
        ${stageFragment}
      `,
      variables,
    ),
  getStage: (id) =>
    studioClient.request(
      gql`
          query stage($id: ID!) {
            stage(id: $id) {
              ...stageFragment
            }
          }
          ${stageFragment}
        `,
      { id },
    ),
  loadStage: (fileLocation, performanceId) =>
    studioClient
      .request(
        gql`
          query ListStage($fileLocation: String, $performanceId: ID) {
            stageList(input: {
              fileLocation: $fileLocation
              performanceId: $performanceId
            }) {
              ...stageFragment
              permission
              scenes {
                ...sceneFragment
              }
            }
          }
          ${stageFragment}
          ${sceneFragment}
        `,
        { fileLocation, performanceId },
      )
      .then((response) => {
        return {
          stage: response.stageList[0]
        };
      }),
  loadPermission: (fileLocation) =>
    client
      .request(
        gql`
          query ListStage($fileLocation: String) {
            stageList(fileLocation: $fileLocation) {
              edges {
                node {
                  permission
                }
              }
            }
          }
        `,
        { fileLocation },
      )
      .then((response) => response.stageList.edges[0]?.node?.permission),
  loadScenes: (fileLocation) =>
    client
      .request(
        gql`
          query ListStage($fileLocation: String) {
            stageList(fileLocation: $fileLocation) {
              edges {
                node {
                  scenes {
                    ...sceneFragment
                  }
                }
              }
            }
          }
          ${sceneFragment}
        `,
        { fileLocation },
      )
      .then((response) => response.stageList.edges[0]?.node?.scenes),
  loadEvents: (fileLocation, cursor) =>
    client
      .request(
        gql`
          query ListStage($fileLocation: String, $cursor: Int) {
            stageList(fileLocation: $fileLocation) {
              edges {
                node {
                  events(cursor: $cursor) {
                    id
                    topic
                    payload
                    mqttTimestamp
                  }
                }
              }
            }
          }
        `,
        { fileLocation, cursor },
      )
      .then((response) => response.stageList.edges[0]?.node?.events),
  uploadMedia: (variables) =>
    studioClient.request(
      gql`
        mutation uploadMedia(
          $name: String!
          $base64: String!
          $mediaType: String
          $filename: String!
        ) {
          uploadMedia(
            name: $name
            base64: $base64
            mediaType: $mediaType
            filename: $filename
          ) {
            asset {
              ...assetFragment
            }
          }
        }
        ${assetFragment}
      `,
      variables,
    ),
  mediaList: (variables) =>
    studioClient.request(
      gql`
        query MediaList($nameLike: String, $mediaType: String) {
          mediaList(
            owner: $nameLike
            mediaType: $mediaType
          ) {
            ...assetFragment
            stages {
              id
              name
              fileLocation
            }
          }
        }
        ${assetFragment}
      `,
      variables,
    ),
  mediaTypeList: (variables) =>
    studioClient.request(
      gql`
        query MediaTypeList {
          mediaTypes {
            id
            name
          }
        }
      `,
      variables,
    ),
  saveStageMedia: (id, mediaIds) =>
    studioClient.request(
      gql`
        mutation SaveStageMedia($id: ID!, $mediaIds: [Int]) {
          assignMedia(input: { id: $id, mediaIds: $mediaIds }) {
            stage {
              ...stageFragment
            }
          }
        }
        ${stageFragment}
      `,
      { id, mediaIds },
    ),
  assignStages: (id, stageIds) =>
    studioClient.request(
      gql`
        mutation AssignStages($id: ID!, $stageIds: [Int]) {
          assignStages(input: { id: $id, stageIds: $stageIds }) {
            asset {
              id
            }
          }
        }
      `,
      { id, stageIds },
    ),
  saveStageConfig: (id, config) =>
    studioClient.request(
      gql`
        mutation UpdateStage($id: ID!, $config: String) {
          updateStage(input: { id: $id, config: $config }) {
            stage {
              ...stageFragment
            }
          }
        }
        ${stageFragment}
      `,
      { id, config },
    ),
  assignableMedia: () =>
    studioClient.request(gql`
      query AssignableMedia {
        avatars: mediaList(mediaType: "avatar") {
          ...assetFragment
        }
        props: mediaList(mediaType: "prop") {
          ...assetFragment
        }
        backdrops: mediaList(mediaType: "backdrop") {
          ...assetFragment
        }
        audios: mediaList(mediaType: "audio") {
          ...assetFragment
        }
        streams: mediaList(mediaType: "stream") {
          ...assetFragment
        }
        curtains: mediaList(mediaType: "curtain") {
          ...assetFragment
        }
      }
      ${assetFragment}
    `),
  updateMedia: (variables) =>
    studioClient.request(
      gql`
        mutation updateMedia(
          $id: ID
          $name: String!
          $mediaType: String
          $description: String
          $fileLocation: String
          $base64: String
          $copyrightLevel: Int
          $playerAccess: String
          $uploadedFrames: [String]
        ) {
          updateMedia(
            id: $id
            name: $name
            mediaType: $mediaType
            description: $description
            fileLocation: $fileLocation
            base64: $base64
            copyrightLevel: $copyrightLevel
            playerAccess: $playerAccess
            uploadedFrames: $uploadedFrames
          ) {
            asset {
              id
            }
          }
        }
      `,
      variables,
    ),
  deleteMedia: (id) =>
    studioClient.request(
      gql`
        mutation deleteMedia($id: ID!) {
          deleteMedia(id: $id) {
            success
            message
          }
        }
      `,
      { id },
    ),
  deleteStage: (id) =>
    studioClient.request(
      gql`
        mutation deleteStage($id: ID!) {
          deleteStage(id: $id) {
            success
          }
        }
      `,
      { id },
    ),
  saveScene: (variables) =>
    studioClient.request(
      gql`
        mutation SaveScene(
          $stageId: ID
          $payload: String
          $preview: String
          $name: String
        ) {
          saveScene(input:{
            stageId: $stageId
            payload: $payload
            preview: $preview
            name: $name
        }) {
            id
          }
        }
      `,
      variables,
    ),
  deleteScene: (id) =>
    studioClient.request(
      gql`
        mutation DeleteScene($id: ID!) {
          deleteScene(id: $id) {
            success
            message
          }
        }
      `,
      { id },
    ),
  duplicateStage: ({ id, name }) =>
    studioClient.request(
      gql`
        mutation duplicateStage($id: ID!, $name: String!) {
          duplicateStage(id: $id, name: $name) {
            id
            name
            description
          }
        }
      `,
      { id, name },
    ),
  deletePerformance: (id) =>
    studioClient.request(
      gql`
        mutation DeletePerformance($id: Int!) {
          deletePerformance(id: $id) {
            success
          }
        }
      `,
      { id },
    ),
  updatePerformance: (id, name, description) =>
    studioClient.request(
      gql`
        mutation updatePerformance(
          $id: Int!
          $name: String
          $description: String
        ) {
          updatePerformance(id: $id, name: $name, description: $description) {
            success
          }
        }
      `,
      { id, name, description },
    ),
  startRecording: (stageId, name, description) =>
    studioClient.request(
      gql`
        mutation startRecording(
          $stageId: ID!
          $name: String
          $description: String
        ) {
          startRecording(
            stageId: $stageId
            name: $name
            description: $description
          ) {
            recording {
              id
            }
          }
        }
      `,
      { stageId, name, description },
    ),
  saveRecording: (id) =>
    studioClient.request(
      gql`
        mutation saveRecording($id: Int!) {
          saveRecording(id: $id) {
            recording {
              id
            }
          }
        }
      `,
      { id },
    ),
  getStreamSign: (key) =>
    client
      .request(
        gql`
          query StreamSign($key: String) {
            assetList(fileLocation: $key) {
              edges {
                node {
                  sign
                }
              }
            }
          }
        `,
        { key },
      )
      .then((response) => response.assetList.edges[0]?.node?.sign),
};
