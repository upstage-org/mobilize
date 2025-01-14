export interface SharedConfigs {
  GRAPHQL_ENDPOINT: string;
  STATIC_ASSETS_ENDPOINT: string;
  STUDIO_ENDPOINT: string;
  AXIOS_TIMEOUT: number;
  ACCESS_TOKEN_KEY: string;
  MQTT_NAMESPACE: string;
  MQTT_CONNECTION: MqttConnection;
  STREAMING: Streaming;
}

export interface MqttConnection {
  url: string;
  username: string;
  password: string;
  clean: boolean;
  connectTimeout: number;
  reconnectPeriod: number;
  retain: boolean;
}

export interface Streaming {
  publish: string;
  subscribe: string;
  auth: Auth;
}

export interface Auth {
  username: string;
  password: string;
}

export interface SharedAuth {
  refresh_token: string;
  token: string;
  username: string;
}
