
const {
  VITE_GRAPHQL_ENDPOINT,
  VITE_STUDIO_ENDPOINT,
  VITE_STATIC_ASSETS_ENDPOINT,
  VITE_CLOUDFLARE_CAPTCHA_SITEKEY,
  VITE_MQTT_NAMESPACE,
  VITE_STREAMING_PUBLISH_ENDPOINT,
  VITE_STREAMING_SUBSCRIBE_ENDPOINT,
  VITE_STREAMING_USERNAME,
  VITE_STREAMING_PASSWORD,
  VITE_MQTT_ENDPOINT,
  VITE_MQTT_USERNAME,
  VITE_MQTT_PASSWORD,
  VITE_JITSI_ENDPOINT
} = import.meta.env;

const configs = {
  MODE: import.meta.env.MODE as "development" | "production",
  UPSTAGE_URL: window.location.origin,
  ALLOWED_EXTENSIONS: {
    IMAGE: ".svg,.jpg,.jpeg,.png,.gif",
    AUDIO: ".wav,.mpeg,.mp3,.aac,.aacp,.ogg,.webm,.flac,.m4a",
    VIDEO: ".mp4,.webm,.opgg,.3gp,.flv",
  },
  ROLES: {
    GUEST: 4,
    PLAYER: 1,
    ADMIN: 8,
    SUPER_ADMIN: 32,
  },
  MEDIA_COPYRIGHT_LEVELS: [
    {
      value: 0,
      name: "✅ Copyright free",
      description:
        "Can be used by other players in any way without need for permission",
    },
    {
      value: 1,
      name: "👌 Use with acknowledgement",
      description:
        "Other players can use the media item as long as the owner is acknowledged",
    },
    {
      value: 2,
      name: "🔐 Use with permission",
      description:
        "Other players must ask the owner for permission if they want to use the media item",
    },
    {
      value: 3,
      name: "🔒️ Not shared",
      description:
        "Only the owner can assign this media item to a stage. Once it is assigned to a stage it can be used there by players who have access to that stage.",
    },
  ],

  GRAPHQL_ENDPOINT: VITE_GRAPHQL_ENDPOINT,
  STUDIO_ENDPOINT: VITE_STUDIO_ENDPOINT,
  STATIC_ASSETS_ENDPOINT: VITE_STATIC_ASSETS_ENDPOINT,
  CLOUDFLARE_CAPTCHA_SITEKEY: VITE_CLOUDFLARE_CAPTCHA_SITEKEY,
  AXIOS_TIMEOUT: 10000,
  JITSI_ENDPOINT: VITE_JITSI_ENDPOINT,
  MQTT_NAMESPACE: VITE_MQTT_NAMESPACE,
  MQTT_CONNECTION: {
    url: VITE_MQTT_ENDPOINT,
    username: VITE_MQTT_USERNAME,
    password: VITE_MQTT_PASSWORD,
    clean: true, // Reserved session
    connectTimeout: 4000, // Time out
    reconnectPeriod: 4000, // Reconnection interval
    retain: true,
  }
};

export default configs;
