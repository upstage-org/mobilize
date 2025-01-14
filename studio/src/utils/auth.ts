// @ts-nocheck
import Cookies from "js-cookie";
import store from "store";
import { computed } from "vue";
import { ROLES } from "./constants";
import { titleCase } from "./common";

const ACCESS_TOKEN = "access_token";
const REFRESH_TOKEN = "refresh_token";

export const setToken = (token) => {
  Cookies.set(ACCESS_TOKEN, JSON.stringify(token), { secure: true });
};
export const getToken = () => Cookies.get(ACCESS_TOKEN);
export const removeToken = () => Cookies.remove(ACCESS_TOKEN);

export const setRefreshToken = (token) => Cookies.set(REFRESH_TOKEN, token);
export const getRefreshToken = () => Cookies.get(REFRESH_TOKEN);
export const removeRefreshToken = () => Cookies.remove(REFRESH_TOKEN);

export const loggedIn = computed(() => store.getters["auth/loggedIn"]);
export const logout = () => store.dispatch("auth/logout");

export function displayName(user) {
  if (!user) return "";
  if (user.displayName?.trim()) return user.displayName;
  if (user.firstName || user.lastName)
    return `${user.firstName ?? ""} ${user.lastName ?? ""}`.trim();
  return user.username;
}

export function displayRole(user) {
  for (const role in ROLES) {
    if (String(ROLES[role]) === String(user.role)) {
      return titleCase(role);
    }
  }
}