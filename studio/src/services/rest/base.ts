// @ts-nocheck
import axios from "axios";
import store from "store";
import { message } from "ant-design-vue";
import config from "config";

const baseURL = new URL(config.API_ENDPOINT).toString();

axios.defaults.baseURL = baseURL;
axios.defaults.timeout = config.AXIOS_TIMEOUT;
axios.defaults.headers.common = {
  Accept: "application/json",
  "Content-Type": "application/json",
};

const requestInterceptor = axios.interceptors.request.use(
  (config) => {
    // do something before request is sent
    const token = store.getters["auth/getToken"] || "";

    if (token && typeof config.headers["X-Access-Token"] === "undefined") {
      config.headers["X-Access-Token"] = token;
    }

    config.headers["Accept"] = "application/json";

    config.headers["Content-Type"] = "application/json";

    config.headers["Access-Control-Allow-Origin"] = "*";

    return config;
  },

  (error) => {
    return Promise.reject(error);
  },
);

const responseInterceptor = axios.interceptors.response.use(
  (response) => ({ ...response, error: null }),
  (error) => {
    const originalRequest = error.config;

    const msg = error?.response?.data?.error;
    if (msg && !originalRequest.hideNotification) {
      let level = error?.response?.data?.level;
      if (!level) {
        level = "error";
      }
      message[level](msg);
    }
    const token = store.getters["auth/getToken"] || "";

    if (
      error?.response?.status === 403 ||
      (error?.response?.status && token && token.length > 0)
    ) {
      if (!originalRequest._retry) {
        return store
          .dispatch("auth/fetchRefreshToken")
          .then((resp) => {
            originalRequest._retry = true;
            return axios.request({
              ...originalRequest,
              headers: {
                Accept: originalRequest.headers.Accept,
                "X-Access-Token": resp,
              },
            });
          })
          .catch(() => {
            store.dispatch("auth/logout");
          });
      }
    }

    return Promise.reject(error);
  },
);

const extend = (config) => {
  const instance = axios.create(config);
  instance.interceptors.request.handlers = axios.interceptors.request.handlers;
  instance.interceptors.response.handlers =
    axios.interceptors.response.handlers;
  return instance;
};

export { baseURL, requestInterceptor, responseInterceptor, extend };
