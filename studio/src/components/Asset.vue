<template>
  <audio controls v-if="asset.mediaType === 'audio'" :src="src"></audio>
  <template v-else-if="asset.mediaType === 'stream'">
    <LarixQRCode v-if="meta.isRTMP" :stream="asset" :size="256" />
    <video v-else controls :src="src"></video>
  </template>
  <img
    v-else
    :src="src"
    style="max-width: 100%; max-height: 100%"
    @load="handleLoad"
  />
</template>

<script>
import { computed } from "vue";
import { absolutePath } from "utils/common";
import LarixQRCode from "components/LarixQRCode.vue";

export default {
  props: ["asset"],
  emits: ["detectSize"],
  components: { LarixQRCode },
  setup: (props, { emit }) => {
    if (props.asset.mediaType) {
      Object.assign(props.asset, { mediaType: props.asset.mediaType.name });
    }
    const src = computed(
      () => props.asset.base64 ?? absolutePath(props.asset.src),
    );
    const meta = computed(() => {
      if (props.asset.description) {
        return JSON.parse(props.asset.description);
      }
      return {};
    });
    const handleLoad = (e) => {
      emit("detectSize", {
        width: e.target.width,
        height: e.target.height,
      });
    };

    return { src, meta, handleLoad };
  },
};
</script>

<style lang="scss" scoped>
audio,
img {
  max-width: 100%;
  max-height: 100%;
}
</style>
