<template>
  <transition name="fade">
    <div v-if="type" class="modal" :class="{ 'is-active': isActive }">
      <div class="modal-background" @click="close"></div>
      <component v-if="simple" :is="type" @close="close" />
      <div v-else ref="modal" class="modal-content">
        <div class="card">
          <a href="#" class="card-header-icon" @click="close">
            <span class="icon">
              <Icon src="close.svg" />
            </span>
          </a>
          <component :is="type" @close="close" />
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { computed, ref } from "vue";
import { useStore } from "vuex";
import ChatBox from "./settings/ChatBox.vue";
import ChatParameters from "./settings/ChatParameters.vue";
import VoiceParameters from "./settings/VoiceParameters.vue";
import SaveScene from "./settings/SaveScene.vue";
import Icon from "components/Icon.vue";
import VolumeParameters from "./settings/VolumeParameters.vue";
import CreateRoom from "./settings/CreateRoom.vue";

export default {
  components: {
    ChatParameters,
    VoiceParameters,
    Icon,
    ChatBox,
    SaveScene,
    VolumeParameters,
    CreateRoom,
  },
  setup: () => {
    const store = useStore();
    const isActive = computed(() => store.state.stage.settingPopup.isActive);
    const type = computed(() => store.state.stage.settingPopup.type);
    const title = computed(() => store.state.stage.settingPopup.title);
    const simple = computed(() => store.state.stage.settingPopup.simple);
    const modal = ref();

    const close = () => {
      store.dispatch("stage/closeSettingPopup");
    };
    return { isActive, close, modal, type, title, simple };
  },
};
</script>
<style scoped lang="scss">
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.card-header-icon {
  position: absolute;
  right: 0;
}
</style>
