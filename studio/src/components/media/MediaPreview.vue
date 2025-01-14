<script lang="ts" setup>
import { PropType, computed, ref } from "vue";
import { Media, MediaAttributes } from "models/studio";
import { absolutePath } from "utils/common";
import LarixQRCode from "components/qrcode/LarixQRCode.vue";
import OBSInstruction from "components/OBSInstruction.vue";

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
    <div v-if="attributes.isRTMP" controls class="w-48">
      <LarixQRCode
        @click="showStreamInstruction = true"
        :stream="media"
        :size="192"
      />
      <a-modal
        v-model:visible="showStreamInstruction"
        :footer="null"
        :width="1000"
      >
        <template #title>
          <h3 class="mb-0">{{ props.media.name }} Setup Info</h3>
        </template>
        <a-row :gutter="12">
          <a-col :span="6">
            <span>Scan this QR Code to start streaming with Larix:</span>
            <div class="flex flex-row justify-center h-full max-h-96">
              <LarixQRCode
                @click="showStreamInstruction = true"
                :stream="media"
                :size="256"
              />
            </div>
          </a-col>
          <a-col :span="18">
            <div class="card-container pr-4">
              <OBSInstruction :url="props.media.fileLocation" :sign="props.media.sign" />
            </div>
          </a-col>
        </a-row>
      </a-modal>
    </div>
    <video v-else controls class="w-48">
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
