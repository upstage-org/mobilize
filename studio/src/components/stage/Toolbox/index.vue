<template>
  <TopBar :tool="tool" />
  <nav id="toolbox" class="panel">
    <div class="panel-body">
      <PanelItem name="Audio" icon="audio.svg" />
      <hr />
      <PanelItem name="Backdrops" icon="backdrop.svg" />
      <PanelItem name="Avatars" icon="avatar.svg" />
      <PanelItem name="Props" icon="prop.svg" />
      <PanelItem name="Streams" label="Video" icon="stream.svg" />
      <PanelItem name="Meeting" label="Streams" icon="meeting.svg" />
      <PanelItem name="Whiteboard" icon="whiteboard.svg" label="Live drawing" />
      <PanelItem name="Draw" icon="object-drawing.svg" label="Object drawing" />
      <PanelItem name="Text" icon="text.svg" />
      <hr />
      <PanelItem name="Depth" icon="depth.svg" />
      <PanelItem name="Curtain" icon="curtain.svg" />
      <PanelItem name="Scenes" icon="animation-slider.svg" />
      <hr />
      <PanelItem name="Settings" icon="configurations.svg" />
      <PlayerChatTool />
    </div>
  </nav>
</template>

<script>
import { computed, provide, ref } from "vue";
import TopBar from "./TopBar.vue";
import PanelItem from "./PanelItem.vue";
import PlayerChatTool from "./PlayerChat.vue";
import { useStore } from "vuex";

export default {
  components: { TopBar, PanelItem, PlayerChatTool },
  setup: () => {
    const tool = ref();
    const store = useStore();
    const changeTool = (newTool) => {
      if (tool.value === newTool) {
        tool.value = undefined;
      } else {
        tool.value = newTool;
      }
      store.commit("stage/SET_ACTIVE_MOVABLE", null);
    };
    provide("tool", tool);
    provide("changeTool", changeTool);

    const isScene = computed(() => tool.value === "Scene");

    return {
      tool,
      changeTool,
      isScene,
    };
  },
};
</script>

<style lang="scss">
#toolbox {
  position: fixed;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  background-color: white;
  opacity: 0.9;
  transition: transform 0.5s;
  z-index: 6;

  hr {
    margin: 0;
  }

  @media only screen and (orientation: portrait) {
    top: 50px !important;
    transform: none !important;
  }

  .panel-icon {
    margin: auto;

    img {
      filter: grayscale(100%);
    }
  }

  .panel-block.is-active,
  .panel-block:hover {
    border: none;

    .panel-icon {
      img {
        filter: none;
      }

      transform: scale(1.5);
    }
  }
}
</style>
