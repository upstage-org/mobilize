// @ts-nocheck
import configs from "config";
import { SharedAuth, SharedConfigs } from "models/config";
import { User as LegacyUser } from "models/studio";
import { message } from "ant-design-vue";

export function absolutePath(path: string) {
  return `${configs.STATIC_ASSETS_ENDPOINT}${path}`;
}

export function getSharedAuth(): SharedAuth | undefined {
  try {
    const sharedStateJSON = localStorage.getItem("vuex");
    if (sharedStateJSON) {
      const sharedState = JSON.parse(sharedStateJSON);
      return sharedState.auth;
    }
  } catch (error) {
    console.log("No shared auth found. Try login using dashboard first!");
  }
}

export function setSharedAuth(auth: SharedAuth) {
  const vuex = JSON.parse(localStorage.getItem("vuex") || "{}");
  localStorage.setItem("vuex", JSON.stringify({ ...vuex, auth }));
}

export function humanFileSize(bytes: number, si = false, dp = 1) {
  const thresh = si ? 1000 : 1024;

  if (Math.abs(bytes) < thresh) {
    return bytes + " B";
  }

  const units = ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  let u = -1;
  const r = 10 ** dp;

  do {
    bytes /= thresh;
    ++u;
  } while (
    Math.round(Math.abs(bytes) * r) / r >= thresh &&
    u < units.length - 1
  );

  return bytes.toFixed(dp) + " " + units[u];
}

export function capitalize(str: string) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}

export function titleCase(str: string) {
  if (!str) {
    return "";
  }
  var splitStr = str.toLowerCase().replace(/_/g, " ").split(" ");
  for (var i = 0; i < splitStr.length; i++) {
    splitStr[i] =
      splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);
  }
  return splitStr.join(" ");
}

export function displayName(
  user: Pick<
    any | LegacyUser,
    "displayName" | "firstName" | "lastName" | "username"
  >,
) {
  if (!user) return "";
  if (user.displayName?.trim()) return user.displayName;
  if (user.firstName || user.lastName)
    return `${user.firstName ?? ""} ${user.lastName ?? ""}`.trim();
  return user.username;
}

export function debounce(callback: TimerHandler, delay: number) {
  let timeout: number;
  return () => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(callback, delay);
  };
}

export function includesIgnoreCase(value: string, keyword: string) {
  return value.toLowerCase().includes(keyword.toLowerCase());
}

export const isJson = (d: any) => {
  try {
    JSON.parse(d);
  } catch (e) {
    return false;
  }
  return true;
};

export const displayTimestamp = (t: number) => {
  let s: any = Math.round(t);
  let m: any = Math.floor(s / 60);
  s = String(s % 60).padStart(2, "0");
  if (m < 60) {
    return `${m}:${s}`;
  }
  let h = Math.floor(m / 60);
  m = String(m % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
};

export function cloneDeep(object: any) {
  return JSON.parse(JSON.stringify(object));
}

export const randomColor = () => {
  var letters = "0123456789ABCDEF";
  var color = "#";
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
};

export const padZero = (str: string, len = 2) => {
  len = len || 2;
  var zeros = new Array(len).join("0");
  return (zeros + str).slice(-len);
};

export const invertColor = (hex: string, bw: boolean) => {
  if (hex.indexOf("#") === 0) {
    hex = hex.slice(1);
  }
  // convert 3-digit hex to 6-digits.
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  }
  if (hex.length !== 6) {
    throw new Error("Invalid HEX color.");
  }
  var r: any = parseInt(hex.slice(0, 2), 16),
    g: any = parseInt(hex.slice(2, 4), 16),
    b: any = parseInt(hex.slice(4, 6), 16);
  if (bw) {
    // http://stackoverflow.com/a/3943023/112731
    return r * 0.299 + g * 0.587 + b * 0.114 > 186 ? "#000000" : "#FFFFFF";
  }
  // invert color components
  r = (255 - r).toString(16);
  g = (255 - g).toString(16);
  b = (255 - b).toString(16);
  // pad each with zeros and return
  return "#" + padZero(r) + padZero(g) + padZero(b);
};

export const randomMessageColor = () => {
  const bg = randomColor();
  const text = invertColor(bg, true);
  return { text, bg };
};

export const randomRange = (min: number, max: number) =>
  Math.floor(Math.random() * (max - min + 1) + min);

export function linkify(inputText: string) {
  var replacedText, replacePattern1, replacePattern2, replacePattern3;

  //URLs starting with http://, https://, or ftp://
  replacePattern1 =
    /(\b(https?|ftp):\/\/[-A-Z0-9+&@#/%?=~_|!:,.;]*[-A-Z0-9+&@#/%=~_|])/gim;
  replacedText = inputText.replace(
    replacePattern1,
    '<a href="$1" target="_blank">$1</a>',
  );

  //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
  replacePattern2 = /(^|[^/])(www\.[\S]+(\b|$))/gim;
  replacedText = replacedText.replace(
    replacePattern2,
    '$1<a href="http://$2" target="_blank">$2</a>',
  );

  //Change email addresses to mailto:: links.
  replacePattern3 = /(([a-zA-Z0-9\-_.])+@[a-zA-Z_]+?(\.[a-zA-Z]{2,6})+)/gim;
  replacedText = replacedText.replace(
    replacePattern3,
    '<a href="mailto:$1">$1</a>',
  );

  return replacedText;
}

export function outOfViewportPosition(el) {
  const rect = el.getBoundingClientRect();
  if (rect.top < 0) {
    return "top";
  }
  if (rect.left < 0) {
    return "left";
  }
  if (
    rect.bottom > (window.innerHeight || document.documentElement.clientHeight)
  ) {
    return "bottom";
  }
  if (
    rect.right > (window.innerWidth || document.documentElement.clientWidth)
  ) {
    return "right";
  }
  return false;
}
export function throttle(callback, limit) {
  let wait = false;
  return function (...args) {
    if (!wait) {
      callback.call(this, ...args);
      wait = true;
      setTimeout(function () {
        wait = false;
      }, limit);
    }
  };
}

export function handleError(e) {
  console.log("====e", e)
  if (e & e.response?.errors && e.response?.errors[0] && e.response?.errors[0].message) {
    message.error(e.response?.errors[0].message)
  } else {
    message.error(typeof e == "string" ? e : "Error!")
  }
}