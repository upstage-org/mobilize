<template>
  <div class="avatar-context-menu card-content p-0">
    <template v-if="holdable">
      <a v-if="isHolding" class="panel-block" @click.stop="releaseAvatar">
        <span class="panel-icon">
          <Icon src="clear.svg" />
        </span>
        <span>{{ $t("release") }}</span>
      </a>
      <a v-else class="panel-block" @click="holdAvatar">
        <span class="panel-icon">
          <Icon src="set-as-avatar.svg" />
        </span>
        <span>{{ $t("hold_this_avatar") }}</span>
      </a>
    </template>
    <template v-else>
      <a v-if="isWearing" class="panel-block" @click="takeOffCostume">
        <span class="panel-icon">
          <Icon src="clear.svg" />
        </span>
        <span>{{ $t("remove_from_avatar") }}</span>
      </a>
      <a v-else-if="currentAvatar && object.type !== 'stream'" class="panel-block" @click="wearCostume">
        <span class="panel-icon">
          <Icon src="prop.svg" />
        </span>
        <span>{{ $t("add_to_avatar") }}</span>
      </a>
    </template>
    <a class="panel-block" @click="bringToFront">
      <span class="panel-icon">
        <Icon src="bring-to-front.svg" />
      </span>
      <span>{{ $t("bring_forward") }}</span>
    </a>
    <a class="panel-block" @click="sendToBack">
      <span class="panel-icon">
        <Icon src="send-to-back.svg" />
      </span>
      <span>{{ $t("send_back") }}</span>
    </a>
    <a v-if="holdable" class="panel-block" @click="changeNickname">
      <span class="panel-icon">
        <Icon src="change-nickname.svg" />
      </span>
      <span>{{ $t("avatar_name") }}</span>
    </a>
    <a v-if="holdable" class="panel-block" @click="openVoiceSetting">
      <span class="panel-icon">
        <Icon src="voice-setting.svg" />
      </span>
      <span>{{ $t("voice_setting") }}</span>
    </a>
    <div class="field has-addons menu-group">
      <p class="control menu-group-title">
        <span class="panel-icon pt-1">
          <Icon src="rotation-slider.svg" />
        </span>
        <span>{{ $t("slider") }}</span>
      </p>
      <p class="control menu-group-item">
        <a-tooltip title="Opacity slider">
          <button class="button is-light" :class="{
            'has-background-primary-light': sliderMode === 'opacity',
          }" @click="changeSliderMode('opacity')">
            <span class="mt-1">
              <Icon src="opacity-slider.svg" />
            </span>
          </button>
        </a-tooltip>
      </p>
      <p v-if="object.multi" class="control menu-group-item">
        <a-tooltip title="Animation speed">
          <button class="button is-light" :class="{
            'has-background-warning-light': sliderMode === 'animation',
          }" @click="changeSliderMode('animation')">
            <span class="mt-1">
              <Icon src="animation-slider.svg" />
            </span>
          </button>
        </a-tooltip>
      </p>
      <p class="control menu-group-item">
        <a-tooltip title="Move speed">
          <button class="button is-light" :class="{
            'has-background-danger-light': sliderMode === 'speed',
          }" @click="changeSliderMode('speed')">
            <span class="mt-1">
              <Icon src="movement-slider.svg" />
            </span>
          </button>
        </a-tooltip>
      </p>
    </div>

    <div class="field has-addons menu-group">
      <p class="control menu-group-title">
        <span class="panel-icon pt-1">
          <Icon src="rotation-slider.svg" />
        </span>
        <span>{{ $t("flip") }}</span>
      </p>
      <p class="control menu-group-item">
        <a-tooltip title="Flip Horizontal">
          <button class="button is-light" :class="{
            'has-background-primary-light': object.scaleX === -1,
          }" @click="flipHorizontal">
            <span class="mt-1">{{ $t("horizontal") }}</span>
          </button>
        </a-tooltip>
      </p>
      <p class="control menu-group-item">
        <a-tooltip title="Flip Vertical">
          <button class="button is-light" :class="{
            'has-background-primary-light': object.scaleY === -1,
          }" @click="flipVertical">
            <span class="mt-1">{{ $t("vertical") }}</span>
          </button>
        </a-tooltip>
      </p>
    </div>
    <template v-if="hasLink">
      <a-tooltip :title="object.link.url">
        <a class="panel-block" @click="openLink">
          <span class="panel-icon">
            <i class="fas fa-link"></i>
          </span>
          <span>{{ $t("open_link") }}</span>
        </a>
      </a-tooltip>
    </template>

    <a class="panel-block has-text-danger" @click="deleteObject">
      <span class="panel-icon">
        <Icon src="remove.svg" />
      </span>
      <span>{{ $t("remove") }}</span>
    </a>
    <a v-if="object.drawingId || object.textId" class="panel-block has-text-danger" @click="deletePermanently">
      <span class="panel-icon">
        <Icon src="remove.svg" />
      </span>
      <span>{{ $t("delete_permanently") }}</span>
    </a>
    <div v-if="object.multi" class="field has-addons menu-group">
      <p class="control menu-group-item" @click="toggleAutoplayFrames()">
        <button class="button is-light">
          <Icon :src="object.autoplayFrames > 0 ? 'pause.svg' : 'play.svg'" />
        </button>
      </p>
      <p v-for="frame in object.frames" :key="frame" @click="switchFrame(frame)" class="control menu-group-item">
        <button class="button is-light">
          <img :src="frame" style="height: 100%" />
        </button>
      </p>
    </div>
  </div>
</template>

<script>
import { useStore } from "vuex";
import { computed, inject, ref } from "vue";
import Icon from "components/Icon.vue";

export default {
  props: [
    "object",
    "closeMenu",
    "active",
    "sliderMode",
    "setSliderMode",
    "keepActive",
  ],
  emits: ["update:active", "hold"],
  components: { Icon },
  setup: (props, { emit }) => {
    const store = useStore();

    const holdAvatar = () => {
      store.dispatch("user/setAvatarId", props.object.id).then(props.closeMenu);
    };

    const releaseAvatar = () => {
      store.dispatch("user/setAvatarId", null).then(props.closeMenu);
    };

    const deleteObject = () => {
      store.dispatch("stage/deleteObject", props.object).then(props.closeMenu);
    };

    const switchFrame = (frame) => {
      store.dispatch("stage/switchFrame", {
        ...props.object,
        src: frame,
      });
    };

    const flipHorizontal = () => {
      const scaleX = -1 * (props.object.scaleX ?? 1);
      store.dispatch("stage/shapeObject", {
        ...props.object,
        scaleX,
      });
    };

    const flipVertical = () => {
      const scaleY = -1 * (props.object.scaleY ?? 1);
      store.dispatch("stage/shapeObject", {
        ...props.object,
        scaleY,
      });
    };

    const toggleAutoplayFrames = () => {
      store
        .dispatch("stage/toggleAutoplayFrames", {
          ...props.object,
          autoplayFrames: props.object.autoplayFrames ? 0 : 100,
        })
        .then(() => {
          emit("update:active", true);
        });
    };

    const changeNickname = () =>
      store
        .dispatch("stage/openSettingPopup", {
          type: "ChatParameters",
        })
        .then(props.closeMenu);

    const bringToFront = () => {
      store.dispatch("stage/bringToFront", props.object).then(props.closeMenu);
    };

    const sendToBack = () => {
      store.dispatch("stage/sendToBack", props.object).then(props.closeMenu);
    };

    const changeSliderMode = (mode) => {
      props.setSliderMode(mode);
      emit("update:active", true);
      props.keepActive(true);
    };

    const holdable = inject("holdable") ?? ref();
    const isHolding = computed(
      () =>
        props.object.holder &&
        props.object.holder.id === store.state.stage.session,
    );

    const openVoiceSetting = () => {
      store
        .dispatch("stage/openSettingPopup", {
          type: "VoiceParameters",
        })
        .then(props.closeMenu);
    };

    const isWearing = inject("isWearing");
    const currentAvatar = computed(() => store.getters["stage/currentAvatar"]);

    const wearCostume = () => {
      if (currentAvatar.value) {
        store
          .dispatch("stage/shapeObject", {
            ...props.object,
            rotate: 0,
            wornBy: currentAvatar.value.id,
          })
          .then(props.closeMenu);
      }
    };

    const takeOffCostume = () => {
      if (isWearing.value) {
        store
          .dispatch("stage/shapeObject", {
            ...props.object,
            wornBy: null,
          })
          .then(props.closeMenu);
      }
    };

    const deletePermanently = () => {
      if (props.object.drawingId) {
        store
          .dispatch("stage/deleteObject", props.object)
          .then(props.closeMenu);
        store.commit("stage/POP_DRAWING", props.object.drawingId);
      }
      if (props.object.textId) {
        store
          .dispatch("stage/deleteObject", props.object)
          .then(props.closeMenu);
        store.commit("stage/POP_TEXT", props.object.textId);
      }
    };

    const hasLink = computed(() => props.object.link && props.object.link.url);
    const openLink = () => {
      const { url, blank } = props.object.link;
      window.open(url, blank ? "_blank" : "_self").focus();
    };

    return {
      switchFrame,
      holdAvatar,
      releaseAvatar,
      deleteObject,
      changeNickname,
      bringToFront,
      sendToBack,
      toggleAutoplayFrames,
      changeSliderMode,
      openVoiceSetting,
      wearCostume,
      takeOffCostume,
      currentAvatar,
      isWearing,
      isHolding,
      holdable,
      deletePermanently,
      flipHorizontal,
      flipVertical,
      hasLink,
      openLink,
    };
  },
};
</script>

<style scoped lang="scss">
.avatar-context-menu {
  * {
    font-size: 14px;
  }

  .panel-block {
    &:hover {
      z-index: 100;
      position: relative;
      font-size: 14px;
    }
  }

  .menu-group {
    width: 100%;
    display: flex;
    margin-bottom: 0;

    .menu-group-title {
      flex: none;
      padding: 6px 12px;
      width: 100px;
      white-space: nowrap;

      >button {
        justify-content: start;
        padding-left: 12px;
      }
    }

    .menu-group-item {
      flex: auto;
    }

    button {
      width: 100%;
    }
  }
}
</style>
