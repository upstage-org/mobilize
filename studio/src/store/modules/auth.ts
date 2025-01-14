// @ts-nocheck
import { userGraph } from "services/graphql";

import {
  setToken,
  removeToken,
  setRefreshToken,
  removeRefreshToken,
} from "utils/auth";
import { message } from "ant-design-vue";

export default {
  namespaced: true,
  state: {
    username: "",
    token: "",
    refresh_token: "",
  },
  mutations: {
    SET_USERNAME(state, data) {
      state.username = data;
    },
    SET_TOKEN(state, data) {
      state.token = data;
    },
    SET_REFRESH_TOKEN(state, data) {
      state.refresh_token = data;
    },
    CLEAR_USER_DATA(state) {
      state.token = "";
      state.refresh_token = "";
    },
  },
  actions: {
    login({ commit }, user) {
      return new Promise((resolve, reject) => {
        userGraph
          .login(user)
          .then((resp) => {
            if (resp?.login?.access_token) {
              const { access_token, refresh_token, username } = resp.login;
              setToken(access_token);
              setRefreshToken(refresh_token);
              commit("SET_USERNAME", username);
              commit("SET_TOKEN", access_token);
              commit("SET_REFRESH_TOKEN", refresh_token);
              resolve();
            } else {
              message.error(
                resp?.errors[0]?.message
              );
              reject(resp);
            }
          }).catch((err) => {
            message.error(
              err.response?.errors ? err.response?.errors[0].message: "Error!"
            );
            reject(err);
          });
      });
    },
    logout({ commit }) {
      commit("CLEAR_USER_DATA");
      localStorage.clear();
      removeToken();
      removeRefreshToken();
      window.location.href = "/";
    },


    // eslint-disable-next-line no-unused-vars
    fetchRefreshToken({ commit, state }) {
      return userGraph
        .refreshUser(
          {
            refreshToken: state.refresh_token,
          },
          {
            "X-Access-Token": state.refresh_token,
          },
        )
        .then((response) => {
          const token = response.refreshToken.access_token;
          commit("SET_TOKEN", token);
          return token;
        });
    },
  },
  getters: {
    loggedIn(state) {
      return !!state.token;
    },
    getToken(state) {
      return state.token;
    },
    getRefreshToken(state) {
      return state.refresh_token;
    },
  },
};
