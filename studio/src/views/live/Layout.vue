<template>
  <div id="live-logo">
    <Logo v-if="loggedIn" :link="studioEndpoint" />
    <Logo v-else to="/" />
  </div>
  <Shell id="main-content">
    <Preloader />
    <template v-if="ready">
      <Board />
      <ReloadStream />
      <ConnectionStatus />
      <MasqueradingStatus />
      <StageToolbox v-if="canPlay" />
      <Chat />
      <PlayerChat v-if="canPlay" />
      <AudioPlayer />
      <LoginPrompt />
      <SettingPopup />
    </template>
  </Shell>
</template>

<script>
import configs from "config";
import Logo from "components/Logo.vue";
import SettingPopup from "components/stage/SettingPopup/index.vue";
import Chat from "components/stage/Chat/index.vue";
import PlayerChat from "components/stage/Chat/PlayerChat.vue";
import StageToolbox from "components/stage/Toolbox/index.vue";
import Board from "components/stage/Board.vue";
import AudioPlayer from "components/stage/AudioPlayer.vue";
import Shell from "components/objects/Meeting/Shell.vue";
import Preloader from "./Preloader.vue";
import LoginPrompt from "./LoginPrompt.vue";
import ConnectionStatus from "./ConnectionStatus.vue";
import MasqueradingStatus from "./MasqueradingStatus.vue";
import { useStore } from "vuex";
import { computed, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { loggedIn } from "utils/auth";
import ReloadStream from "./ReloadStream.vue";

export default {
  components: {
    Logo,
    Preloader,
    LoginPrompt,
    SettingPopup,
    Chat,
    PlayerChat,
    StageToolbox,
    Board,
    AudioPlayer,
    ConnectionStatus,
    MasqueradingStatus,
    Shell,
    ReloadStream
  },
  setup: () => {
    const store = useStore();
    const ready = computed(() => store.getters["stage/ready"]);

    const route = useRoute();
    store.dispatch("stage/loadStage", { url: route.params.url }).then(() => {
      store.dispatch("stage/connect");
    });

    onUnmounted(() => {
      store.dispatch("stage/disconnect");
    });

    window.addEventListener("beforeunload", () => {
      store.dispatch("stage/disconnect");
    });

    const canPlay = computed(() => store.getters["stage/canPlay"]);

    return {
      ready,
      canPlay,
      loggedIn,
      studioEndpoint: configs.STUDIO_ENDPOINT,
    };
  },
};
</script>

<style lang="scss">
#main-content {
  min-height: calc(100vh - 120px);
}

#live-stage {
  *:not(input, textarea) {
    -webkit-user-select: none;
    /* Safari */
    user-select: none;
    /* Non-prefixed version, currently supported by Chrome, Edge, Opera and Firefox */
  }
}

#live-logo {
  position: fixed;
  right: 0px;
  max-width: 200px;
  z-index: 1;

  &.preloader {
    z-index: 20001;
  }

  @media screen and (min-width: 1024px) {
    img {
      max-height: unset;
    }
  }
}
</style>
