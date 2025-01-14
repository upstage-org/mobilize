<template>
  <div class="dropdown is-hoverable">
    <div class="dropdown-trigger">
      <Upload v-if="!active" v-model="base64" @change="handleFileChange">
        <span>{{ $t("new") }}</span>
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
      </Upload>
    </div>
  </div>
  <Modal width="100%" height="100%" v-model="active">
    <MediaModal v-if="media" :media="media" @complete="uploadCompleted" />
  </Modal>
</template>

<script>
import Modal from "components/Modal.vue";
import Upload from "components/form/Upload.vue";
import MediaModal from "./MediaModal.vue";
import { ref } from "@vue/reactivity";
import { inject } from "@vue/runtime-core";

export default {
  props: ["special"],
  components: { Modal, MediaModal, Upload },
  setup: () => {
    const base64 = ref();
    const active = ref();

    const media = ref();

    const getType = (fileType) => {
      if (fileType === "image") return "avatar";
      if (fileType === "audio") return "audio";
      if (fileType === "video") return "stream";
    };

    const handleFileChange = async (file, type) => {
      if (file) {
        active.value = true;
        media.value = {
          name: file.name,
          base64: base64.value,
          mediaType: getType(type),
          fileType: type,
          filename: file.name,
          stages: [],
          copyrightLevel: 0,
        };
      }
    };

    const refresh = inject("refresh");
    const uploadCompleted = () => {
      refresh();
      media.value = null;
    };

    return {
      active,
      base64,
      media,
      handleFileChange,
      uploadCompleted,
    };
  },
};
</script>

<style></style>