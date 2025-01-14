// @ts-nocheck
import moment from "moment";
import { v4 as uuidv4 } from "uuid";
import hash from "object-hash";
import buildClient from "services/mqtt";
import {
  absolutePath,
  cloneDeep,
  randomColor,
  randomMessageColor,
  randomRange,
} from "utils/common";
import {
  TOPICS,
  BOARD_ACTIONS,
  BACKGROUND_ACTIONS,
  COLORS,
  DRAW_ACTIONS,
} from "utils/constants";
import {
  deserializeObject,
  recalcFontSize,
  serializeObject,
  unnamespaceTopic,
  getDefaultStageConfig,
  getDefaultStageSettings,
} from "./reusable";
import { getViewport } from "./reactiveViewport";
import { stageGraph } from "services/graphql";
import { useAttribute } from "services/graphql/composable";
import { avatarSpeak, stopSpeaking } from "services/speech";
import anime from "animejs";
import { Promise } from "core-js";

const mqtt = buildClient();

export default {
  namespaced: true,
  state: {
    preloading: true,
    model: null,
    background: null,
    curtain: null,
    backdropColor: "gray",
    chatPosition: "right",
    status: "OFFLINE",
    subscribeSuccess: false,
    activeMovable: null,
    chat: {
      messages: [],
      privateMessages: [],
      privateMessage: "",
      color: randomMessageColor(),
      opacity: 0.9,
      fontSize: "14px",
      playerFontSize: "14px",
    },
    board: {
      objects: [],
      drawings: [],
      texts: [],
      whiteboard: [],
      tracks: [],
    },
    tools: {
      avatars: [],
      props: [],
      backdrops: [],
      audios: [],
      streams: [],
      meetings: [],
      curtains: [],
    },
    config: getDefaultStageConfig(),
    settings: getDefaultStageSettings(), // Settings will be saved as part of scene, while config is not
    settingPopup: {
      isActive: false,
    },
    preferences: {
      isDrawing: false,
      text: {
        fontSize: "20px",
        fontFamily: "Josefin Sans",
      },
    },
    reactions: [],
    viewport: getViewport(),
    sessions: [],
    session: null,
    replay: {
      timestamp: {
        begin: 0,
        end: 0,
        current: 0,
      },
      timers: [],
      interval: null,
      speed: 1,
    },
    loadingRunningStreams: false,
    audioPlayers: [],
    isSavingScene: false,
    isLoadingScenes: false,
    showPlayerChat: false,
    showClearChatSetting: false,
    showDownloadChatSetting: false,
    lastSeenPrivateMessage: localStorage.getItem("lastSeenPrivateMessage") ?? 0,
    runningStreams: [],
    masquerading: false,
    purchasePopup: {
      isActive: false,
    },
  },
  getters: {
    ready(state) {
      return state.model && !state.preloading;
    },
    url(state) {
      return state.model ? state.model.fileLocation : "demo";
    },
    objects(state) {
      return state.board.objects.map((o) => ({
        ...o,
        holder: state.sessions.find((s) => s.avatarId === o.id),
      }));
    },
    config(state) {
      return state.config;
    },
    preloadableAssets(state) {
      const assets = []
        .concat(state.tools.avatars.map((a) => a.src))
        .concat(state.tools.avatars.map((a) => a.frames ?? []).flat())
        .concat(state.tools.props.map((p) => p.src))
        .concat(state.tools.props.map((a) => a.frames ?? []).flat())
        .concat(state.tools.backdrops.map((b) => b.src))
        .concat(state.tools.backdrops.map((a) => a.frames ?? []).flat())
        .concat(state.tools.curtains.map((b) => b.src));
      return assets;
    },
    audios(state) {
      return state.tools.audios;
    },
    currentAvatar(state, getters, rootState) {
      const id = rootState.user.avatarId;
      return state.board.objects.find((o) => o.id === id);
    },
    activeMovable(state) {
      if (state.masquerading) {
        return null;
      }
      return state.activeMovable;
    },
    stageSize(state, getters) {
      let width = state.viewport.width;
      let height = state.viewport.height;
      let left = 0;
      let top = 0;
      const ratio = getters.config.ratio;
      if (width / height > ratio) {
        width = height * ratio;
        left = (window.innerWidth - width) / 2;
      } else {
        height = width / ratio;
        if (window.innerWidth < window.innerHeight) {
          // Portrait mobile
          top = 0;
        } else {
          top = (window.innerHeight - height) / 2;
        }
      }
      return { width, height, left, top };
    },
    canPlay(state) {
      return (
        state.model &&
        state.model.permission &&
        state.model.permission !== "audience" &&
        !state.replay.isReplaying &&
        !state.masquerading &&
        !state.replay.isReplaying
      );
    },
    players(state) {
      return state.sessions.filter((s) => s.isPlayer);
    },
    audiences(state) {
      return state.sessions.filter((s) => !s.isPlayer);
    },
    unreadPrivateMessageCount(state) {
      return state.chat.privateMessages.filter(
        (m) => m.at > state.lastSeenPrivateMessage,
      ).length;
    },
    whiteboard(state) {
      return state.board.whiteboard;
    },
    jitsiTracks(state) {
      return state.board.tracks;
    },
  },
  mutations: {
    SET_MODEL(state, model) {
      state.model = model;
      if (model) {
        const media = model.media;
        if (media && media.length) {
          media.forEach((item) => {
            if (item.description) {
              const meta = JSON.parse(item.description);
              delete item.description;
              Object.assign(item, meta);
            }
            if (item.type === "stream") {
              item.url = absolutePath(item.src);
              delete item.src;
            } else {
              item.src = absolutePath(item.src);
            }
            if (item.multi) {
              item.frames = item.frames.map((src) => absolutePath(src));
            }
            const key = item.type + "s";
            if (!state.tools[key]) {
              state.tools[key] = [];
            }
            state.tools[key].push(item);
          });
        } else {
          state.preloading = false;
        }
        const config = useAttribute({ value: model }, "config", true).value;
        if (config) {
          Object.assign(state.config, config);
          state.config.ratio = config.ratio.width / config.ratio.height;
        }
        const cover = useAttribute({ value: model }, "cover", false).value;
        state.model.cover = cover && absolutePath(cover);
      }
    },
    CLEAN_STAGE(state, cleanModel) {
      if (cleanModel) {
        state.model = null;
        state.tools.audios = [];
      }
      state.status = "OFFLINE";
      state.replay.isReplaying = false;
      state.background = null;
      state.curtain = null;
      state.backdropColor = "gray";
      state.tools.avatars = [];
      state.tools.props = [];
      state.tools.backdrops = [];
      state.tools.streams = [];
      state.tools.curtains = [];
      state.config = getDefaultStageConfig();
      state.settings = getDefaultStageSettings();
      state.board.objects = [];
      state.board.drawings = [];
      state.board.texts = [];
      state.board.whiteboard = [];
      state.chat.messages = [];
      state.chat.privateMessages = [];
      state.chat.color = randomColor();
    },
    SET_BACKGROUND(state, background) {
      if (background) {
        if (
          !state.background ||
          !state.background.at ||
          state.background.at < background.at
        ) {
          if (!state.background || state.background.id !== background.id) {
            // Not playing animation if only opacity change
            anime({
              targets: "#board",
              opacity: [0, 1],
              duration: 5000,
            });
          }
          state.background = background;
        }
      }
    },
    SET_STATUS(state, status) {
      state.status = status;
    },
    SET_SUBSCRIBE_STATUS(state, status) {
      state.subscribeSuccess = status;
    },
    PUSH_CHAT_MESSAGE(state, message) {
      message.hash = hash(message);
      const lastMessage = state.chat.messages[state.chat.messages.length - 1];
      if (lastMessage && lastMessage.hash === message.hash) {
        return;
      }
      state.chat.messages.push(message);
    },
    PUSH_PLAYER_CHAT_MESSAGE(state, message) {
      message.hash = hash(message);
      const lastMessage =
        state.chat.privateMessages[state.chat.privateMessages.length - 1];
      if (lastMessage && lastMessage.hash === message.hash) {
        return;
      }
      state.chat.privateMessages.push(message);
    },
    CLEAR_CHAT(state) {
      state.chat.messages.length = 0;
    },
    CLEAR_PLAYER_CHAT(state) {
      state.chat.privateMessages.length = 0;
    },
    REMOVE_MESSAGE(state, id) {
      state.chat.messages = state.chat.messages.filter((m) => m.id !== id);
    },
    HIGHLIGHT_MESSAGE(state, id) {
      const message = state.chat.messages.find((m) => m.id === id);
      if (message) {
        message.highlighted = !message.highlighted;
      }
    },
    PUSH_OBJECT(state, object) {
      const { id } = object;
      deserializeObject(object);
      const model = state.board.objects.find((o) => o.id === id);
      if (model) {
        Object.assign(model, object);
      } else {
        state.board.objects.push(object);
      }
    },
    UPDATE_OBJECT(state, object) {
      const { id } = object;
      deserializeObject(object);
      const model = state.board.objects.find((o) => o.id === id);
      if (model) {
        const deltaX = object.x - model.x;
        const deltaY = object.y - model.y;
        const deltaW = object.w / model.w;
        const deltaH = object.h / model.h;
        const deltaRotate = object.rotate - model.rotate;
        const costumes = state.board.objects.filter((o) => o.wornBy === id);
        if (costumes.length) {
          costumes.forEach((costume) => {
            costume.moveSpeed = object.moveSpeed;
            costume.opacity = object.opacity;
            costume.liveAction = object.liveAction;
            const offsetX = costume.x - model.x;
            const offsetY = costume.y - model.y;
            costume.x += deltaX + offsetX * deltaW - offsetX;
            costume.y += deltaY + offsetY * deltaH - offsetY;
            costume.w *= deltaW;
            costume.h *= deltaH;
            costume.rotate += deltaRotate;
          });
        }
        Object.assign(model, object);
      }
    },
    DELETE_OBJECT(state, object) {
      const { id } = object;
      state.board.objects = state.board.objects.filter((o) => o.id !== id);
      state.board.objects
        .filter((o) => o.wornBy === id)
        .forEach((costume) => {
          costume.wornBy = null;
        });
    },
    SET_OBJECT_SPEAK(state, { avatar, speak, mute }) {
      const { id } = avatar;
      let model = state.board.objects.find((o) => o.id === id);
      if (model) {
        speak.hash = hash(speak);
        if (model.speak?.hash !== speak.hash) {
          model.speak = speak;
          if (!mute && (state.status === "LIVE" || state.replay.isReplaying)) {
            avatarSpeak(model, speak.message);
          }
          setTimeout(
            () => {
              if (model.speak?.message === speak.message) {
                model.speak = null;
              }
            },
            1000 + speak.message.split(" ").length * 1000,
          );
        }
      }
    },
    SET_PRELOADING_STATUS(state, status) {
      state.preloading = status;
    },
    UPDATE_AUDIO(state, audio) {
      const model = state.tools.audios.find((a) => a.src === audio.src);
      if (model) {
        audio.changed = true;
        Object.assign(model, audio);
      }
    },
    SET_SETTING_POPUP(state, setting) {
      state.settingPopup = setting;
    },
    SEND_TO_BACK(state, object) {
      const index = state.board.objects.findIndex(
        (avatar) => avatar.id === object.id,
      );
      if (index > -1) {
        state.board.objects.unshift(state.board.objects.splice(index, 1)[0]);
      }
    },
    BRING_TO_FRONT(state, object) {
      const index = state.board.objects.findIndex(
        (avatar) => avatar.id === object.id,
      );
      if (index > -1) {
        state.board.objects.push(state.board.objects.splice(index, 1)[0]);
      }
    },
    BRING_TO_FRONT_OF(state, { front, back }) {
      const frontIndex = state.board.objects.findIndex(
        (avatar) => avatar.id === front,
      );
      const backIndex = state.board.objects.findIndex(
        (avatar) => avatar.id === back,
      );
      if (frontIndex > -1 && backIndex > -1) {
        state.board.objects.splice(
          backIndex,
          0,
          state.board.objects.splice(frontIndex, 1)[0],
        );
      }
    },
    SET_PREFERENCES(state, preferences) {
      Object.assign(state.preferences, preferences);
    },
    PUSH_DRAWING(state, drawing) {
      state.board.drawings.push(cloneDeep(drawing));
    },
    POP_DRAWING(state, drawingId) {
      state.board.drawings = state.board.drawings.filter(
        (d) => d.drawingId !== drawingId,
      );
    },
    PUSH_TEXT(state, text) {
      state.board.texts.push(text);
    },
    POP_TEXT(state, textId) {
      state.board.texts = state.board.texts.filter((d) => d.textId !== textId);
    },
    PUSH_STREAM_TOOL(state, stream) {
      state.tools.streams.push(stream);
    },
    PUSH_RUNNING_STREAMS(state, streams) {
      state.runningStreams = streams;
    },
    UPDATE_IS_DRAWING(state, isDrawing) {
      state.preferences.isDrawing = isDrawing;
    },
    UPDATE_IS_WRITING(state, isWriting) {
      state.preferences.isWriting = isWriting;
    },
    UPDATE_TEXT_OPTIONS(state, options) {
      Object.assign(state.preferences.text, options);
    },
    PUSH_REACTION(state, reaction) {
      state.reactions.push({
        reaction,
        x: randomRange(150, window.innerWidth) - 300,
        y: window.innerHeight - 100,
      });
      setTimeout(() => {
        state.reactions.shift();
      }, state.config.reactionDuration);
    },
    UPDATE_VIEWPORT(state, viewport) {
      state.viewport = viewport;
    },
    RESCALE_OBJECTS(state, ratio) {
      state.board.objects.forEach((object) => {
        object.x = object.x * ratio;
        object.y = object.y * ratio;
        object.w = object.w * ratio;
        object.h = object.h * ratio;
        recalcFontSize(object, (s) => s * ratio);
      });
    },
    SET_CHAT_PARAMETERS(state, { opacity, fontSize }) {
      state.chat.opacity = opacity;
      state.chat.fontSize = fontSize;
    },
    SET_PLAYER_CHAT_PARAMETERS(state, { playerFontSize }) {
      state.chat.playerFontSize = playerFontSize;
    },
    UPDATE_SESSIONS_COUNTER(state, session) {
      const index = state.sessions.findIndex((s) => s.id === session.id);
      if (index > -1) {
        if (session.leaving) {
          return state.sessions.splice(index, 1);
        } else {
          Object.assign(state.sessions[index], session);
        }
      } else {
        state.sessions.push(session);
      }
      state.sessions = state.sessions.filter(
        (s) => moment().diff(moment(new Date(s.at)), "minute") < 60,
      );
      state.sessions.sort((a, b) => b.at - a.at);
    },
    SET_CHAT_VISIBILITY(state, visible) {
      state.settings.chatVisibility = visible;
    },
    SET_DARK_MODE_CHAT(state, enabled) {
      state.settings.chatDarkMode = enabled;
    },
    SET_REACTION_VISIBILITY(state, visible) {
      state.settings.reactionVisibility = visible;
    },
    SET_CHAT_POSITION(state, position) {
      state.chatPosition = position;
    },
    SET_BACKDROP_COLOR(state, color) {
      state.backdropColor = color;
    },
    SET_REPLAY(state, replay) {
      Object.assign(state.replay, replay);
    },
    SET_ACTIVE_MOVABLE(state, id) {
      state.activeMovable = id;
    },
    UPDATE_AUDIO_PLAYER_STATUS(state, { index, ...status }) {
      if (!state.audioPlayers[index]) {
        state.audioPlayers[index] = {};
      }
      Object.assign(state.audioPlayers[index], status);
    },
    SET_CURTAIN(state, curtain) {
      state.curtain = curtain;
    },
    REPLACE_SCENE(state, { payload }) {
      anime({
        targets: "#live-stage",
        filter: ["brightness(0)", "brightness(1)"],
        easing: "linear",
        duration: 3000,
      });
      state.activeMovable = null;
      if (payload) {
        const snapshot = JSON.parse(payload);
        snapshot.board.objects.forEach(deserializeObject);
        snapshot.board.tracks = state.board.tracks;
        snapshot.backdropColor = state.config?.defaultcolor || COLORS.DEFAULT_BACKDROP;

        Object.keys(snapshot).forEach((key) => {
          if (
            key == "audioPlayers" &&
            snapshot[key].length == 0 &&
            state[key].length > 0
          ) {
            state[key].forEach((audioPlayer) => {
              audioPlayer.currentTime = 0;
            });
          } else {
            state[key] = snapshot[key];
          }
        });
      }
    },
    SET_SAVING_SCENE(state, value) {
      state.isSavingScene = value;
    },
    SET_SHOW_PLAYER_CHAT(state, value) {
      state.showPlayerChat = value;
    },
    SET_SHOW_CLEAR_CHAT_SETTINGS(state, value) {
      state.showClearChatSetting = value;
    },
    SET_SHOW_DOWNLOAD_CHAT_SETTINGS(state, value) {
      state.showDownloadChatSetting = value;
    },
    TAG_PLAYER(state, player) {
      state.chat.privateMessage += `@${player.nickname.trim()}`;
    },
    SEEN_PRIVATE_MESSAGES(state) {
      const length = state.chat.privateMessages.length;
      if (length > 0) {
        state.lastSeenPrivateMessage =
          state.chat.privateMessages[length - 1].at;
        localStorage.setItem(
          "lastSeenPrivateMessage",
          state.lastSeenPrivateMessage,
        );
      }
    },
    UPDATE_WHITEBOARD(state, message) {
      if (!state.board.whiteboard) {
        state.board.whiteboard = [];
      }
      switch (message.type) {
        case DRAW_ACTIONS.NEW_LINE:
          state.board.whiteboard = state.board.whiteboard.concat(
            message.command,
          );
          break;
        case DRAW_ACTIONS.UNDO:
          state.board.whiteboard = state.board.whiteboard.filter(
            (e, i) => i !== message.index,
          );
          break;
        case DRAW_ACTIONS.CLEAR:
          state.board.whiteboard = [];
          break;
        default:
          break;
      }
    },
    TOGGLE_MASQUERADING(state) {
      state.masquerading = !state.masquerading;
    },
    CREATE_ROOM(state, room) {
      state.tools.meetings.push(room);
    },
    CREATE_STREAM(state, room) {
      state.tools.streams.push(room);
    },
    REORDER_TOOLBOX(state, { from, to }) {
      console.log(from, to);
      if (from.scenePreview) {
        // is scene
        const fromIndex = state.model.scenes.findIndex((t) => t.id === from.id);
        const toIndex = state.model.scenes.findIndex((t) => t.id === to.id);
        if (fromIndex > -1 && toIndex > -1) {
          const tool = state.model.scenes.splice(fromIndex, 1)[0];
          state.model.scenes.splice(toIndex, 0, tool);
        }
      } else if (from.drawingId) {
        // is drawing
        const fromIndex = state.board.drawings.findIndex(
          (t) => t.drawingId === from.drawingId,
        );
        const toIndex = state.board.drawings.findIndex(
          (t) => t.drawingId === to.drawingId,
        );
        if (fromIndex > -1 && toIndex > -1) {
          const tool = state.board.drawings.splice(fromIndex, 1)[0];
          state.board.drawings.splice(toIndex, 0, tool);
        }
      } else if (from.textId) {
        // is text
        const fromIndex = state.board.texts.findIndex(
          (t) => t.textId === from.textId,
        );
        const toIndex = state.board.texts.findIndex(
          (t) => t.textId === to.textId,
        );
        if (fromIndex > -1 && toIndex > -1) {
          const tool = state.board.texts.splice(fromIndex, 1)[0];
          state.board.texts.splice(toIndex, 0, tool);
        }
      } else {
        const toolName = from.type + "s";
        if (state.tools[toolName]) {
          const fromIndex = state.tools[toolName].findIndex(
            (t) => t.id === from.id,
          );
          const toIndex = state.tools[toolName].findIndex(
            (t) => t.id === to.id,
          );
          if (fromIndex > -1 && toIndex > -1) {
            const tool = state.tools[toolName].splice(fromIndex, 1)[0];
            state.tools[toolName].splice(toIndex, 0, tool);
          }
        }
      }
    },
    SET_PURCHASE_POPUP(state, purchase) {
      state.purchasePopup = purchase;
    },
    ADD_TRACK(state, track) {
      state.board.tracks = [...state.board.tracks, track];
    },
  },
  actions: {
    connect({ commit, dispatch }) {
      commit("SET_STATUS", "CONNECTING");

      const client = mqtt.connect();
      client.on("connect", () => {
        commit("SET_STATUS", "LIVE");
        dispatch("reloadMissingEvents");
        dispatch("subscribe");
        dispatch("joinStage");
      });
      client.on("error", () => {
        commit("SET_STATUS", "OFFLINE");
      });
      client.on("close", () => {
        commit("SET_STATUS", "OFFLINE");
      });
      client.on("disconnect", () => {
        commit("SET_STATUS", "OFFLINE");
      });
      client.on("offline", () => {
        commit("SET_STATUS", "OFFLINE");
      });
      mqtt.receiveMessage((payload) => {
        dispatch("handleMessage", payload);
      });
    },
    subscribe({ commit }) {
      const topics = {
        [TOPICS.CHAT]: { qos: 2 },
        [TOPICS.BOARD]: { qos: 2 },
        [TOPICS.BACKGROUND]: { qos: 2 },
        [TOPICS.AUDIO]: { qos: 2 },
        [TOPICS.REACTION]: { qos: 2 },
        [TOPICS.COUNTER]: { qos: 2 },
        [TOPICS.DRAW]: { qos: 2 },
      };
      mqtt
        .subscribe(topics)
        .then((res) => {
          commit("SET_SUBSCRIBE_STATUS", true);
          console.log("Subscribed to topics: ", res);
        })
        .catch((error) => console.log(error));
    },
    async disconnect({ dispatch }) {
      await dispatch("leaveStage", true);
      mqtt.disconnect();
    },
    handleMessage({ dispatch }, { topic, message }) {
      switch (topic) {
        case TOPICS.CHAT:
          dispatch("handleChatMessage", { message });
          break;
        case TOPICS.BOARD:
          dispatch("handleBoardMessage", { message });
          break;
        case TOPICS.BACKGROUND:
          dispatch("handleBackgroundMessage", { message });
          break;
        case TOPICS.AUDIO:
          dispatch("handleAudioMessage", { message });
          break;
        case TOPICS.REACTION:
          dispatch("handleReactionMessage", { message });
          break;
        case TOPICS.COUNTER:
          dispatch("handleCounterMessage", { message });
          break;
        case TOPICS.DRAW:
          dispatch("handleDrawMessage", { message });
          break;
        default:
          break;
      }
    },
    sendChat({ state, rootGetters, getters }, { message, isPrivate }) {
      if (!message) return;
      let user = rootGetters["user/chatname"];
      let isPlayer = getters["canPlay"];
      let behavior = "speak";
      const session = state.session;
      if (message.startsWith(":")) {
        behavior = "think";
        message = message.substr(1);
      }
      if (message.startsWith("!")) {
        behavior = "shout";
        message = message.substr(1).toUpperCase();
      }
      if (isPlayer && message.startsWith("-")) {
        message = message.substr(1);
        const fakeName = message.split(" ")[0];
        if (fakeName) {
          user = fakeName;
          message = message.substr(fakeName.length).trim();
        }
        isPlayer = false;
      }
      const payload = {
        user,
        message: message,
        behavior,
        isPlayer,
        isPrivate,
        session,
        at: +new Date(),
        id: uuidv4(),
      };
      mqtt.sendMessage(TOPICS.CHAT, payload);
      const avatar = getters["currentAvatar"];
      if (avatar && isPlayer && !isPrivate) {
        mqtt.sendMessage(TOPICS.BOARD, {
          type: BOARD_ACTIONS.SPEAK,
          avatar,
          speak: payload,
        });
      }
    },
    handleChatMessage({ commit, state, rootGetters, dispatch }, { message }) {
      if (message.clear) {
        commit("CLEAR_CHAT");
        return;
      }
      if (message.clearPlayerChat) {
        commit("CLEAR_PLAYER_CHAT");
        return;
      }
      if (message.remove) {
        commit("REMOVE_MESSAGE", message.remove);
        return;
      }
      if (message.highlight) {
        commit("HIGHLIGHT_MESSAGE", message.highlight);
        return;
      }

      const model = {
        user: "Anonymous",
        color: "#000000",
      };
      if (typeof message === "object") {
        Object.assign(model, message);
      } else {
        model.message = message;
      }
      if (message.isPrivate) {
        commit("PUSH_PLAYER_CHAT_MESSAGE", model);
        if (message.at > state.lastSeenPrivateMessage) {
          if (state.showPlayerChat) {
            commit("SEEN_PRIVATE_MESSAGES");
          } else {
            const nickname = rootGetters["user/nickname"];
            if (
              message.message
                .toLowerCase()
                .includes(`@${nickname.trim().toLowerCase()}`)
            ) {
              dispatch("showPlayerChat", true);
            }
          }
        }
      } else {
        commit("PUSH_CHAT_MESSAGE", model);
      }
    },
    placeObjectOnStage({ commit, dispatch, state }, data) {
      const object = {
        w: 100,
        h: 100,
        opacity: 1,
        moveSpeed: 2000,
        voice: {},
        volume: 100,
        rotate: 0,
        ...data,
        id: uuidv4(),
      };
      if (object.type === "stream") {
        object.hostId = state.session;
      }
      commit("PUSH_OBJECT", serializeObject(object));
      if (data.type === "avatar") {
        dispatch("user/setAvatarId", object.id, { root: true }).then(() => {
          commit("SET_ACTIVE_MOVABLE", null);
        });
      }
      return object;
    },
    shapeObject({ commit, state }, object) {
      if (object.liveAction) {
        if (object.published) {
          mqtt.sendMessage(TOPICS.BOARD, {
            type: BOARD_ACTIONS.MOVE_TO,
            object: serializeObject(object),
          });
        } else {
          object.published = true;
          mqtt.sendMessage(TOPICS.BOARD, {
            type: BOARD_ACTIONS.PLACE_OBJECT_ON_STAGE,
            object: serializeObject(object),
          });
        }
        state.board.objects
          .filter((o) => o.wornBy === object.id)
          .forEach((costume) => {
            if (!costume.published) {
              costume.published = true;
              mqtt.sendMessage(TOPICS.BOARD, {
                type: BOARD_ACTIONS.PLACE_OBJECT_ON_STAGE,
                object: serializeObject(costume),
              });
            }
          });
      } else {
        commit("UPDATE_OBJECT", serializeObject(object));
      }
    },
    deleteObject(action, object) {
      object = serializeObject(object);
      if (object.drawingId) {
        // is drawing
        delete object.commands;
      }
      const payload = {
        type: BOARD_ACTIONS.DESTROY,
        object,
      };
      mqtt.sendMessage(TOPICS.BOARD, payload);
    },
    switchFrame(action, object) {
      const payload = {
        type: BOARD_ACTIONS.SWITCH_FRAME,
        object: serializeObject(object),
      };
      mqtt.sendMessage(TOPICS.BOARD, payload);
    },
    sendToBack(action, object) {
      const payload = {
        type: BOARD_ACTIONS.SEND_TO_BACK,
        object: serializeObject(object),
      };
      mqtt.sendMessage(TOPICS.BOARD, payload);
    },
    bringToFront(action, object) {
      const payload = {
        type: BOARD_ACTIONS.BRING_TO_FRONT,
        object: serializeObject(object),
      };
      mqtt.sendMessage(TOPICS.BOARD, payload);
    },
    bringToFrontOf(action, { front, back }) {
      const payload = {
        type: BOARD_ACTIONS.BRING_TO_FRONT_OF,
        front,
        back,
      };
      mqtt.sendMessage(TOPICS.BOARD, payload);
    },
    toggleAutoplayFrames(action, object) {
      const payload = {
        type: BOARD_ACTIONS.TOGGLE_AUTOPLAY_FRAMES,
        object: serializeObject(object),
      };
      mqtt.sendMessage(TOPICS.BOARD, payload);
    },
    handleBoardMessage({ commit }, { message }) {
      switch (message.type) {
        case BOARD_ACTIONS.PLACE_OBJECT_ON_STAGE:
          commit("PUSH_OBJECT", message.object);
          break;
        case BOARD_ACTIONS.MOVE_TO:
          commit("UPDATE_OBJECT", message.object);
          break;
        case BOARD_ACTIONS.DESTROY:
          commit("DELETE_OBJECT", message.object);
          break;
        case BOARD_ACTIONS.SWITCH_FRAME:
          commit("UPDATE_OBJECT", message.object);
          break;
        case BOARD_ACTIONS.SPEAK:
          commit("SET_OBJECT_SPEAK", message);
          break;
        case BOARD_ACTIONS.SEND_TO_BACK:
          commit("SEND_TO_BACK", message.object);
          break;
        case BOARD_ACTIONS.BRING_TO_FRONT:
          commit("BRING_TO_FRONT", message.object);
          break;
        case BOARD_ACTIONS.BRING_TO_FRONT_OF:
          commit("BRING_TO_FRONT_OF", message);
          break;
        case BOARD_ACTIONS.TOGGLE_AUTOPLAY_FRAMES:
          commit("UPDATE_OBJECT", message.object);
          break;
        default:
          break;
      }
    },
    setBackground(action, background) {
      background.at = +new Date();
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.CHANGE_BACKGROUND,
        background,
      });
    },
    showChatBox(action, visible) {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.SET_CHAT_VISIBILITY,
        visible,
      });
    },
    enableDarkModeChat(action, enabled) {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.SET_DARK_MODE_CHAT,
        enabled,
      });
    },
    showReactionsBar(action, visible) {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.SET_REACTION_VISIBILITY,
        visible,
      });
    },
    setChatPosition(action, position) {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.SET_CHAT_POSITION,
        position,
      });
    },
    setBackdropColor(action, color) {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.SET_BACKDROP_COLOR,
        color,
      });
    },
    drawCurtain(action, curtain) {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.DRAW_CURTAIN,
        curtain,
      });
    },
    loadScenes() {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.LOAD_SCENES,
      });
    },
    switchScene(action, scene) {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.SWITCH_SCENE,
        scene,
      });
    },
    blankScene() {
      mqtt.sendMessage(TOPICS.BACKGROUND, {
        type: BACKGROUND_ACTIONS.BLANK_SCENE,
      });
    },
    handleBackgroundMessage({ commit, dispatch }, { message }) {
      switch (message.type) {
        case BACKGROUND_ACTIONS.CHANGE_BACKGROUND:
          commit("SET_BACKGROUND", message.background);
          break;
        case BACKGROUND_ACTIONS.SET_CHAT_VISIBILITY:
          commit("SET_CHAT_VISIBILITY", message.visible);
          break;
        case BACKGROUND_ACTIONS.SET_DARK_MODE_CHAT:
          commit("SET_DARK_MODE_CHAT", message.enabled);
          break;
        case BACKGROUND_ACTIONS.SET_REACTION_VISIBILITY:
          commit("SET_REACTION_VISIBILITY", message.visible);
          break;
        case BACKGROUND_ACTIONS.SET_CHAT_POSITION:
          commit("SET_CHAT_POSITION", message.position);
          break;
        case BACKGROUND_ACTIONS.SET_BACKDROP_COLOR:
          commit("SET_BACKDROP_COLOR", message.color);
          break;
        case BACKGROUND_ACTIONS.DRAW_CURTAIN:
          commit("SET_CURTAIN", message.curtain);
          break;
        case BACKGROUND_ACTIONS.LOAD_SCENES:
          dispatch("reloadScenes");
          break;
        case BACKGROUND_ACTIONS.SWITCH_SCENE:
          dispatch("replaceScene", message.scene);
          break;
        case BACKGROUND_ACTIONS.BLANK_SCENE:
          commit("REPLACE_SCENE", {
            payload: JSON.stringify({
              background: null,
              backdropColor: "gray",
              board: {
                objects: [],
                drawings: [],
                texts: [],
                tracks: [],
              },
              audioPlayers: [],
            }),
          });
          break;
        default:
          break;
      }
    },
    updateAudioStatus(_, audio) {
      mqtt.sendMessage(TOPICS.AUDIO, audio);
    },
    handleAudioMessage({ commit }, { message }) {
      commit("UPDATE_AUDIO", message);
    },
    closeSettingPopup({ commit }) {
      commit("SET_SETTING_POPUP", { isActive: false });
    },
    openSettingPopup({ commit }, setting) {
      setting.isActive = true;
      commit("SET_SETTING_POPUP", setting);
    },
    addDrawing({ commit, dispatch }, drawing) {
      commit("PUSH_DRAWING", drawing);
      dispatch("placeObjectOnStage", drawing);
    },
    addStream({ commit, dispatch }, stream) {
      stream.type = "stream";
      commit("PUSH_STREAM_TOOL", stream);
      dispatch("placeObjectOnStage", stream);
    },
    addText({ commit, dispatch }, text) {
      text.type = "text";
      commit("PUSH_TEXT", text);
      dispatch("placeObjectOnStage", text);
    },
    handleReactionMessage({ commit }, { message }) {
      commit("PUSH_REACTION", message);
    },
    sendReaction(_, reaction) {
      mqtt.sendMessage(TOPICS.REACTION, reaction);
    },
    async loadStage({ commit, dispatch }, { url, recordId }) {
      commit("CLEAN_STAGE", true);
      commit("SET_PRELOADING_STATUS", true);
      const { stage } = await stageGraph.loadStage(url, recordId);
      if (stage) {
        commit("SET_MODEL", stage);
        const { events } = stage;
        if (recordId && events) {
          commit("SET_REPLAY", {
            timestamp: {
              begin: events[0].mqttTimestamp,
              current: events[0].mqttTimestamp,
              end: events[events.length - 1].mqttTimestamp,
            },
          });
        } else {
          (events || []).forEach((event) => dispatch("replayEvent", event));
        }
      } else {
        commit("SET_PRELOADING_STATUS", false);
      }
    },
    async reloadPermission({ state }) {
      const { stage } = await stageGraph.loadStage(state.model.fileLocation);
      // const permission = await stageGraph.loadPermission(
      //   state.model.fileLocation,
      // );
      if (stage) {
        state.model.permission = stage.permission;
      }
    },
    async loadPermission({ state, commit }) {
      const permission = state.model.permission;
      //  await stageGraph.loadPermission(
      //   state.model.fileLocation,
      // );
      if (permission == "owner" || permission == "editor") {
        commit("SET_SHOW_CLEAR_CHAT_SETTINGS", true);
        commit("SET_SHOW_DOWNLOAD_CHAT_SETTINGS", true);
      } else {
        commit("SET_SHOW_CLEAR_CHAT_SETTINGS", false);
        commit("SET_SHOW_DOWNLOAD_CHAT_SETTINGS", false);
      }
    },
    async reloadScenes({ state }) {
      state.isLoadingScenes = true;
      const scenes = await stageGraph.loadScenes(state.model.fileLocation);
      if (scenes) {
        state.model.scenes = scenes;
      }
      state.isLoadingScenes = false;
    },
    async reloadMissingEvents({ state, dispatch }) {
      if (state.model.events) {
        const lastEventId =
          state.model.events[state.model.events.length - 1]?.id ?? 0;
        const events = await stageGraph.loadEvents(
          state.model.fileLocation,
          lastEventId,
        );
        if (events) {
          events.forEach((event) => dispatch("replicateEvent", event));
          state.model.events = state.model.events.concat(events);
        }
      }
    },
    replaceScene({ state, commit, dispatch }, sceneId) {
      anime({
        targets: "#live-stage",
        filter: "brightness(0)",
      });
      const scene = state.model.scenes.find((s) => s.id == sceneId);
      if (scene) {
        commit("REPLACE_SCENE", scene);
      } else {
        if (state.isLoadingScenes) {
          setTimeout(() => dispatch("replaceScene", sceneId), 1000); // If the scene is not loaded completely, retry after 1 second
        } else {
          commit("REPLACE_SCENE", { payload: null });
        }
      }
    },
    replayEvent({ dispatch }, { topic, payload }) {
      dispatch("handleMessage", {
        topic: unnamespaceTopic(topic),
        message: JSON.parse(payload),
      });
    },
    replicateEvent({ dispatch }, { topic, payload }) {
      const message = JSON.parse(payload);
      message.mute = true;
      dispatch("handleMessage", {
        topic: unnamespaceTopic(topic),
        message,
      });
    },
    async replayRecording({ state, dispatch, commit }, timestamp) {
      stopSpeaking();
      await dispatch("pauseReplay");
      const current = timestamp
        ? Number(timestamp)
        : state.replay.timestamp.begin;
      state.replay.timestamp.current = current;
      commit("CLEAN_STAGE");
      state.replay.isReplaying = true;
      const events = state.model.events;
      const speed = state.replay.speed;
      state.replay.interval = setInterval(() => {
        state.replay.timestamp.current += 1;
        if (state.replay.timestamp.current > state.replay.timestamp.end) {
          state.replay.timestamp.current = state.replay.timestamp.begin;
          dispatch("pauseReplay");
        }
      }, 1000 / speed);
      events.forEach((event) => {
        if (event.mqttTimestamp - current >= 0) {
          const timer = setTimeout(
            () => {
              dispatch("replayEvent", event);
            },
            ((event.mqttTimestamp - current) * 1000) / speed,
          );
          state.replay.timers.push(timer);
        } else {
          dispatch("replicateEvent", event);
        }
      });
    },
    pauseReplay({ state }) {
      clearInterval(state.replay.interval);
      state.replay.interval = null;
      state.replay.timers.forEach((timer) => clearTimeout(timer));
      state.replay.timers = [];
      state.tools.audios.forEach((audio) => {
        audio.isPlaying = false;
        audio.changed = true;
      });
    },
    seekForwardReplay({ state, dispatch }) {
      const current = state.replay.timestamp.current + 10000;
      const nextEvent = state.model.events.find(
        (e) => e.mqttTimestamp > current,
      );
      if (nextEvent) {
        dispatch("replayRecording", nextEvent.mqttTimestamp);
      }
    },
    seekBackwardReplay({ state, dispatch }) {
      const current = state.replay.timestamp.current - 10000;
      let event = null;
      for (let i = state.model.events.length - 1; i >= 0; i--) {
        event = state.model.events[i];
        if (event.mqttTimestamp < current) {
          break;
        }
      }
      if (event) {
        dispatch("replayRecording", event.mqttTimestamp);
      }
    },
    handleCounterMessage({ commit, state }, { message }) {
      commit("UPDATE_SESSIONS_COUNTER", message);
      if (message.id === state.session && message.avatarId) {
        commit("user/SET_AVATAR_ID", message.avatarId, { root: true });
      }
    },
    async joinStage({ rootGetters, state, rootState, commit, dispatch }) {
      if (!state.session) {
        state.session = rootState.user.user?.id ?? uuidv4();
      }
      const id = state.session;
      const isPlayer = rootGetters["auth/loggedIn"];
      const nickname = rootGetters["user/nickname"];
      const avatarId = rootGetters["user/avatarId"];
      commit("SET_ACTIVE_MOVABLE", avatarId);
      const at = +new Date();
      const payload = { id, isPlayer, nickname, at, avatarId };
      await mqtt.sendMessage(TOPICS.COUNTER, payload);
      await dispatch("sendStatistics");
    },
    async leaveStage({ dispatch }) {
      await Promise.all([
        dispatch("sendStatisticsBeforeDisconnect"),
        dispatch("sendCounterLeave"),
      ]);
    },
    async sendStatisticsBeforeDisconnect({ rootGetters }) {
      const isPlayer = rootGetters["auth/loggedIn"];
      let players = rootGetters["stage/players"].length;
      let audiences = rootGetters["stage/audiences"].length;
      if (isPlayer) {
        players = players - 1;
      } else {
        audiences = audiences - 1;
      }
      await mqtt.sendMessage(
        TOPICS.STATISTICS,
        { players: players, audiences: audiences },
        false,
        true,
      );
    },
    async sendCounterLeave({ state, commit }) {
      const id = state.session;
      state.session = null;
      commit("CLEAN_STAGE");
      await mqtt.sendMessage(TOPICS.COUNTER, { id, leaving: true });
    },
    async sendStatistics({ state, getters }) {
      if (state.subscribeSuccess) {
        await mqtt.sendMessage(
          TOPICS.STATISTICS,
          {
            players: getters.players.length,
            audiences: getters.audiences.length,
          },
          false,
          true,
        );
      }
    },
    clearChat() {
      mqtt.sendMessage(TOPICS.CHAT, { clear: true });
    },
    clearPlayerChat() {
      mqtt.sendMessage(TOPICS.CHAT, { clearPlayerChat: true });
    },
    removeChat(action, messageId) {
      mqtt.sendMessage(TOPICS.CHAT, { remove: messageId });
    },
    highlightChat(action, messageId) {
      mqtt.sendMessage(TOPICS.CHAT, { highlight: messageId });
    },
    showPlayerChat({ commit }, visible) {
      commit("SET_SHOW_PLAYER_CHAT", visible);
      if (visible) {
        commit("SEEN_PRIVATE_MESSAGES");
      }
    },
    autoFocusMoveable({ commit, getters, state }, id) {
      if (
        getters.canPlay &&
        !state.preferences.isDrawing &&
        !state.replay.isReplaying
      ) {
        commit("SET_ACTIVE_MOVABLE", id);
      }
    },
    handleDrawMessage({ commit }, { message }) {
      commit("UPDATE_WHITEBOARD", message);
    },
    sendDrawWhiteboard(action, command) {
      mqtt.sendMessage(TOPICS.DRAW, { type: DRAW_ACTIONS.NEW_LINE, command });
    },
    sendUndoWhiteboard({ state }) {
      mqtt.sendMessage(TOPICS.DRAW, {
        type: DRAW_ACTIONS.UNDO,
        index: state.board.whiteboard.length - 1,
      });
    },
    sendClearWhiteboard() {
      mqtt.sendMessage(TOPICS.DRAW, { type: DRAW_ACTIONS.CLEAR });
    },
    closePurchasePopup({ commit }) {
      commit("SET_PURCHASE_POPUP", { isActive: false });
    },
    openPurchasePopup({ commit }, setting) {
      setting.isActive = true;
      commit("SET_PURCHASE_POPUP", setting);
    },
    addTrack({ commit }, track) {
      commit("ADD_TRACK", track);
    },
  },
};
