const {
  VUE_APP_API_ENDPOINT,
  VUE_APP_GRAPHQL_ENDPOINT,
  VUE_APP_STATIC_ASSETS_ENDPOINT,
  VUE_APP_STUDIO_ENDPOINT,
  VUE_APP_MQTT_NAMESPACE,
  VUE_APP_MQTT_ENDPOINT,
  VUE_APP_MQTT_USERNAME,
  VUE_APP_MQTT_PASSWORD,
  VUE_APP_STREAMING_PUBLISH_ENDPOINT,
  VUE_APP_STREAMING_SUBSCRIBE_ENDPOINT,
  VUE_APP_STREAMING_USERNAME,
  VUE_APP_STREAMING_PASSWORD,
  VUE_APP_JITSI_ENDPOINT,
  VUE_APP_CLOUDFLARE_CAPTCHA_SITEKEY,
} = process.env;

let configs = {
  API_ENDPOINT: VUE_APP_API_ENDPOINT,
  GRAPHQL_ENDPOINT: VUE_APP_GRAPHQL_ENDPOINT,
  STATIC_ASSETS_ENDPOINT: VUE_APP_STATIC_ASSETS_ENDPOINT,
  STUDIO_ENDPOINT: VUE_APP_STUDIO_ENDPOINT,
  JITSI_ENDPOINT: VUE_APP_JITSI_ENDPOINT,
  AXIOS_TIMEOUT: 10000,
  ACCESS_TOKEN_KEY: "access_token",
  MQTT_NAMESPACE: VUE_APP_MQTT_NAMESPACE,
  CLOUDFLARE_CAPTCHA_SITEKEY: VUE_APP_CLOUDFLARE_CAPTCHA_SITEKEY,
  MQTT_CONNECTION: {
    url: VUE_APP_MQTT_ENDPOINT,
    username: VUE_APP_MQTT_USERNAME,
    password: VUE_APP_MQTT_PASSWORD,
    clean: true, // Reserved session
    connectTimeout: 4000, // Time out
    reconnectPeriod: 4000, // Reconnection interval
    retain: true,
  },
  STREAMING: {
    publish: VUE_APP_STREAMING_PUBLISH_ENDPOINT,
    subscribe: VUE_APP_STREAMING_SUBSCRIBE_ENDPOINT,
    auth: {
      username: VUE_APP_STREAMING_USERNAME,
      password: VUE_APP_STREAMING_PASSWORD,
    },
  },
};

localStorage.setItem("configs", JSON.stringify(configs));

export default configs;
