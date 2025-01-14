<script lang="ts" setup>
import { PropType, computed, ref } from "vue";
import { Media, MediaAttributes } from "models/studio";
import { absolutePath } from "utils/common";

const props = defineProps({
  media: {
    type: Object as PropType<Media>,
    required: true,
  },
});

const attributes = computed<MediaAttributes>(() => {
  return JSON.parse(props.media.description || "{}");
});

const showStreamInstruction = ref(false);
</script>

<template>
  <audio v-if="props.media.assetType.name === 'audio'" controls class="w-48">
    <source :src="absolutePath(props.media.fileLocation)" />
    Your browser does not support the audio element.
  </audio>
  <template v-else-if="props.media.assetType.name === 'stream'">
    <video controls class="w-48">
      <source :src="absolutePath(props.media.fileLocation)" />
      Your browser does not support the video tag.
    </video>
  </template>
  <template v-else>
    <a-image
      :src="absolutePath(props.media.fileLocation)"
      class="w-24 max-h-24 object-contain"
    />
    <a-popover v-if="attributes.multi" placement="right">
      <template #title>
        <b>{{ $t("multiframes") }}</b>
        <br />
        <span>Total frames: {{ attributes.frames.length }}</span>
      </template>
      <template #content>
        <div class="flex p-2 w-96">
          <div v-for="frame in attributes.frames" :key="frame" class="m-1">
            <a-image :src="absolutePath(frame)" />
          </div>
        </div>
      </template>
      <img
        src="assets/multi-frame.svg"
        alt="Multiframe"
        class="absolute left-4 bottom-4"
      />
    </a-popover>
  </template>
</template>

<style scoped>
.ant-carousel :deep(.slick-dots) {
  position: relative;
  height: auto;
}
.ant-carousel :deep(.slick-slide img) {
  border: 5px solid #fff;
  display: block;
  margin: auto;
  max-width: 80%;
}
.ant-carousel :deep(.slick-arrow) {
  display: none !important;
}
.ant-carousel :deep(.slick-thumb) {
  bottom: 0px;
  display: flex;
}
.ant-carousel :deep(.slick-thumb li) {
  width: 45px;
}
.ant-carousel :deep(.slick-thumb li img) {
  width: 100%;
  height: 100%;
  transform: scale(0.8);
}
.ant-carousel :deep(.slick-thumb li.slick-active img) {
  transform: scale(1);
}
</style>
