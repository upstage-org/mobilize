import { absolutePath } from "@/utils/common";
import { gql } from "graphql-request";
import { stageGraph } from ".";
import { createClient } from "./graphql";

const client = createClient('stage_graphql')

export const stageFragment = gql`
  fragment stageFragment on Stage {
    id
    name
    fileLocation
    description
    permission
    owner {
      id
      username
      displayName
    }
    attributes {
      id
      name
      description
    }
    media {
      id
      name
      type
      src
      description
    }
    dbId
  }
`

export const assetFragment = gql`
  fragment assetFragment on Asset {
    id
    name
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
    createdOn
    src
    dbId
    copyrightLevel
    playerAccess
    permission
    sign
  }
`

export const sceneFragment = gql`
  fragment sceneFragment on Scene {
    id
    name
    payload
    scenePreview
  }
`

export default {
  createStage: async (variables) => {
    let result = await client.request(gql`
      mutation CreateStage($name: String, $fileLocation: String) {
        createStage(input: {name: $name, fileLocation: $fileLocation}) {
          stage {
            id
          }
        }
      }
    `, variables);
    if (result) {
      variables.id = result.createStage.stage.id
      result = await stageGraph.updateStage(variables)
      return result.updateStage.stage
    }
  },
  updateStage: (variables) => client.request(gql`
    mutation UpdateStage($id: ID!, $name: String, $description: String, $fileLocation: String, $status: String, $cover: String, $playerAccess: String) {
      updateStage(input: {id: $id, name: $name, description: $description, fileLocation: $fileLocation, status: $status, cover: $cover, playerAccess: $playerAccess}) {
        stage {
          ...stageFragment
        }
      }
    }
    ${stageFragment}
  `, variables),
  sweepStage: (variables) => client.request(gql`
    mutation SweepStage($id: ID!) {
      sweepStage(input: {id: $id}) {
        success
        performanceId
      }
    }
  `, variables),
  stageList: (variables) => client.request(gql`
    query ListStage($id: ID, $nameLike: String, $fileLocation: String) {
      stageList(id: $id, nameLike: $nameLike, fileLocation: $fileLocation) {
        totalCount
        edges {
          node {
            ...stageFragment
            activeRecording {
              id
              name
              createdOn
            }
          }
        }
      }
    }
    ${stageFragment}
  `, variables),
  getStage: (id) => client.request(gql`
    query ListStage($id: ID) {
      stageList(id: $id) {
        edges {
          node {
            ...stageFragment
            chats {
              payload
              performanceId
            }
            performances {
              id
              createdOn
              name
              description
              recording
            }
            scenes {
              id
              name
              scenePreview
              createdOn
              owner {
                id
                username
                displayName
              }
            }
          }
        }
      }
    }
    ${stageFragment}
  `, { id }),
  loadStage: (fileLocation, performanceId) => client.request(gql`
    query ListStage($fileLocation: String, $performanceId: Int) {
      stageList(fileLocation: $fileLocation) {
        edges {
          node {
            ...stageFragment
            events(performanceId: $performanceId) {
              id
              topic
              payload
              mqttTimestamp
            }
            scenes(performanceId: $performanceId) {
              ...sceneFragment
            }
          }
        }
      }
      curtains: assetList(assetType: "curtain") {
        edges {
          node {
            name
            fileLocation
          }
        }
      },
    }
    ${stageFragment}
    ${sceneFragment}
  `, { fileLocation, performanceId }).then(response => {
    const path = edge => ({
      name: edge.node.name,
      src: absolutePath(edge.node.fileLocation)
    })
    return {
      stage: response.stageList.edges[0]?.node,
      curtains: response.curtains.edges.map(path)
    }
  }),
  loadPermission: (fileLocation) => client.request(gql`
    query ListStage($fileLocation: String) {
      stageList(fileLocation: $fileLocation) {
        edges {
          node {
            permission
          }
        }
      }
    }
  `, { fileLocation }).then(response => response.stageList.edges[0]?.node?.permission),
  loadScenes: (fileLocation) => client.request(gql`
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
  `, { fileLocation }).then(response => response.stageList.edges[0]?.node?.scenes),
  loadEvents: (fileLocation, cursor) => client.request(gql`
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
  `, { fileLocation, cursor }).then(response => response.stageList.edges[0]?.node?.events),
  uploadMedia: (variables) => client.request(gql`
    mutation uploadMedia($name: String!, $base64: String!, $mediaType: String, $filename: String!) {
      uploadMedia(name: $name, base64: $base64, mediaType: $mediaType, filename: $filename) {
        asset {
          ...assetFragment
        }
      }
    }
    ${assetFragment}
  `, variables),
  mediaList: (variables) => client.request(gql`
    query AssetList($id: ID, $nameLike: String, $assetType: String) {
      assetList(id: $id, nameLike: $nameLike, assetType: $assetType, sort: ID_DESC) {
        edges {
          node {
            ...assetFragment
            stages {
              id
              name
              url
            }
          }
        }
      }
    }
    ${assetFragment}
  `, variables),
  assetTypeList: (variables) => client.request(gql`
    query AssetTypeList($id: ID, $nameLike: String) {
      assetTypeList(id: $id, nameLike: $nameLike) {
        edges {
          node {
            id
            dbId
            name
          }
        }
      }
    }
  `, variables),
  saveStageMedia: (id, mediaIds) => client.request(gql`
    mutation SaveStageMedia($id: ID!, $mediaIds: [Int]) {
      assignMedia(input: {id: $id, mediaIds: $mediaIds}) {
        stage {
          ...stageFragment
        }
      }
    }
    ${stageFragment}
  `, { id, mediaIds }),
  assignStages: (id, stageIds) => client.request(gql`
    mutation AssignStages($id: ID!, $stageIds: [Int]) {
      assignStages(input: {id: $id, stageIds: $stageIds}) {
        asset {
          id
        }
      }
    }
  `, { id, stageIds }),
  saveStageConfig: (id, config) => client.request(gql`
    mutation UpdateStage($id: ID!, $config: String) {
      updateStage(input: {id: $id, config: $config}) {
        stage {
          ...stageFragment
        }
      }
    }
    ${stageFragment}
  `, { id, config }),
  assignableMedia: () => client.request(gql`
    query AssignableMedia {
      avatars: assetList(assetType: "avatar") {
        edges {
          node {
            ...assetFragment
          }
        }
      }
      props: assetList(assetType: "prop") {
        edges {
          node {
            ...assetFragment
          }
        }
      }
      backdrops: assetList(assetType: "backdrop") {
        edges {
          node {
            ...assetFragment
          }
        }
      }
      audios: assetList(assetType: "audio") {
        edges {
          node {
            ...assetFragment
          }
        }
      }
      streams: assetList(assetType: "stream") {
        edges {
          node {
            ...assetFragment
          }
        }
      }
    }
    ${assetFragment}
  `),
  updateMedia: (variables) => client.request(gql`
    mutation updateMedia($id: ID, $name: String!, $mediaType: String, $description: String, $fileLocation: String, $base64: String, $copyrightLevel: Int, $playerAccess: String, $uploadedFrames: [String]) {
      updateMedia(id: $id, name: $name, mediaType: $mediaType, description: $description, fileLocation: $fileLocation, base64: $base64, copyrightLevel: $copyrightLevel, playerAccess: $playerAccess, uploadedFrames: $uploadedFrames) {
        asset {
          id
        }
      }
    }  
  `, variables),
  deleteMedia: (id) => client.request(gql`
    mutation deleteMedia($id: ID!) {
      deleteMedia(id: $id) {
        success
        message
      }
    }
  `, { id }),
  deleteStage: (id) => client.request(gql`
    mutation deleteStage($id: ID!) {
      deleteStage(id: $id) {
        success
      }
    }
  `, { id }),
  saveScene: (variables) => client.request(gql`
    mutation SaveScene($stageId: Int!, $payload: String, $preview: String, $name: String) {
      saveScene(stageId: $stageId, payload: $payload, preview: $preview, name: $name) {
        id
      }
    }
  `, variables),
  deleteScene: (id) => client.request(gql`
    mutation DeleteScene($id: Int!) {
      deleteScene(id: $id) {
        success
        message
      }
    }  
  `, { id }),
  duplicateStage: ({ id, name }) => client.request(gql`
    mutation duplicateStage($id: ID!, $name: String!) {
      duplicateStage(id: $id, name: $name) {
        success,
        newStageId
      }
    }
  `, { id, name }),
  deletePerformance: (id) => client.request(gql`
    mutation DeletePerformance($id: Int!) {
      deletePerformance(id: $id) {
        success
      }
    }  
  `, { id }),
  updatePerformance: (id, name, description) => client.request(gql`
    mutation updatePerformance($id: Int!, $name: String, $description: String) {
      updatePerformance(id: $id, name: $name, description: $description) {
        success
      }
    }
  `, { id, name, description }),
  startRecording: (stageId, name, description) => client.request(gql`
    mutation startRecording($stageId: ID!, $name: String, $description: String) {
      startRecording(stageId: $stageId, name: $name, description: $description) {
        recording {
          id
        }
      }
    }
  `, { stageId, name, description }),
  saveRecording: (id) => client.request(gql`
    mutation saveRecording($id: Int!) {
      saveRecording(id: $id) {
        recording {
          id
        }
      }
    }
  `, { id }),
  getStreamSign: key => client.request(gql`
    query StreamSign($key: String) {
      assetList(fileLocation: $key) {
        edges {
          node {
            sign
          }
        }
      }
    }
  `, { key }).then(response => response.assetList.edges[0]?.node?.sign)
}