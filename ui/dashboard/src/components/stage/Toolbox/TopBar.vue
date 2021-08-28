<template>
  <div id="topbar" class="card is-light" v-if="tool">
    <div
      ref="bar"
      class="card-content"
      :class="{ 'is-compact': compact }"
      :id="tool + 'tool'"
      @wheel="horizontalScroll"
    >
      <component :is="tool" />
    </div>
  </div>
</template>

<script>
import { onUnmounted, ref } from "vue";
import Avatars from "./tools/Avatars";
import Backdrops from "./tools/Backdrops";
import Props from "./tools/Props";
import Audio from "./tools/Audio";
import Draw from "./tools/Draw/index";
import Whiteboard from "./tools/Whiteboard";
import Streams from "./tools/Streams/index";
import Text from "./tools/Text";
import Settings from "./tools/Settings";
import Depth from "./tools/Depth";
import Curtain from "./tools/Curtain";
import Scenes from "./tools/Scenes";

export default {
  props: ["tool"],
  components: {
    Avatars,
    Backdrops,
    Props,
    Audio,
    Draw,
    Streams,
    Text,
    Settings,
    Depth,
    Curtain,
    Scenes,
    Whiteboard,
  },
  setup: () => {
    const bar = ref();
    const horizontalScroll = (e) => {
      bar.value.scrollLeft += e.deltaY * 10;
      bar.value.scrollLeft += e.deltaX;
    };

    const compact = ref(false);

    const toggleCompact = (e) => {
      if (!e) e = window.event;
      if (e.shiftKey) {
        compact.value = true;
      } else {
        compact.value = false;
      }
    };
    window.addEventListener("keydown", toggleCompact);
    window.addEventListener("keyup", toggleCompact);

    onUnmounted(() => {
      window.removeEventListener("keydown", toggleCompact);
      window.removeEventListener("keyup", toggleCompact);
    });

    return { horizontalScroll, bar, compact };
  },
};
</script>

<style lang="scss">
@import "@/styles/bulma";
@import "@/styles/mixins";

#topbar {
  display: flex;
  flex: 1;
  position: fixed;
  max-width: 80vw;
  height: 100px;
  top: -12px;
  left: 0;
  right: 0;
  margin: auto;
  text-align: center;
  width: fit-content;
  overflow: auto;
  z-index: 2;

  .card-content {
    display: flex;
    padding: 0;
    padding-top: 12px;
    min-height: min-content;
    white-space: nowrap;

    &.is-compact {
      width: 100%;
    }

    > div {
      position: relative;
      width: 100px;
      height: 88px;
      padding: 12px;
      background: $light;

      &:first-child {
        float: left;
      }

      .tag {
        height: 1.5em;
        padding: 0;
        box-shadow: none;
      }

      &:hover,
      &.active {
        cursor: pointer;
        filter: brightness(1.2);
        background-color: lightgray;
        img {
          -webkit-filter: drop-shadow(5px 5px 5px $dark);
          filter: drop-shadow(5px 5px 5px $dark);
        }
        .tag {
          background-color: transparent;
        }
      }
    }
  }
}
</style>