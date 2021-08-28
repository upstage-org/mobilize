<template>
  <div class="file">
    <label class="file-label has-tooltip-right" :data-tooltip="tooltip">
      <input
        :id="id"
        class="file-input"
        type="file"
        name="resume"
        :accept="accept"
        @input="handleInputFile"
      />
      <span class="file-cta">
        <slot>
          <span class="file-icon">
            <i class="fas fa-file"></i>
          </span>
          <span class="file-label">Choose a file…</span>
        </slot>
      </span>
      <div v-if="!valid" class="mt-2 mx-2 has-text-danger">
        <span>Maximum file size: {{ humanFileSize(mediaLimit) }}&nbsp;</span>
        <i class="fas fa-times"></i>
        (current size: {{ humanFileSize(file.size) }})
      </div>
    </label>
  </div>

  <template v-if="preview && file">
    <img v-if="isImage" :src="modelValue" alt="Preview" />
    <div v-else class="box has-text-centered">
      <i class="fas fa-file"></i>
      <b>{{ file.name }} ({{ humanFileSize(file.size) }})</b>
    </div>
  </template>
</template>

<script>
import { ref } from "@vue/reactivity";
import { computed, watch } from "@vue/runtime-core";
import { humanFileSize } from "@/utils/common";
import { useStore } from "vuex";
import { imageExtensions, audioExtensions, videoExtensions } from "@/utils/constants";
export default {
  props: {
    modelValue: String,
    id: String,
    initialFile: Object,
    type: String,
    preview: Boolean,
  },
  emits: ["update:modelValue", "change"],
  setup: (props, { emit }) => {
    const store = useStore();
    const nginxLimit = computed(() => store.getters["config/uploadLimit"]);
    const mediaLimit = computed(() => {
      let limit = store.state.user.user?.uploadLimit;
      if (!limit || props.acceptVideo) {
        limit = nginxLimit.value;
      }
      return limit;
    });
    const file = ref(props.initialFile);

    const accept = computed(() => {
      let extensions = [];
      if (props.type === "image" || !props.type) {
        extensions.push(imageExtensions);
      }
      if (props.type === "audio" || !props.type) {
        extensions.push(audioExtensions);
      }
      if (props.type === "video" || !props.type) {
        extensions.push(videoExtensions);
      }
      return extensions.join(",");
    });

    const valid = computed(() => {
      if (file.value) {
        return file.value.size <= mediaLimit.value;
      }
      return true;
    });

    const type = computed(() => {
      if (file.value) {
        const parts = file.value.name.split(".");
        const extension = parts[parts.length - 1];
        if (imageExtensions.includes(extension)) {
          return "image";
        }
        if (audioExtensions.includes(extension)) {
          return "audio";
        }
        if (videoExtensions.includes(extension)) {
          return "video";
        }
      }
      return null;
    });

    watch(
      () => props.modelValue,
      (value) => {
        if (!value) {
          file.value = null;
        }
      }
    );

    watch(mediaLimit, () => {
      if (!valid.value) {
        emit("change", null);
      }
    });

    const handleInputFile = (e) => {
      const reader = new FileReader();
      reader.readAsDataURL(e.target.files[0]);
      reader.onload = () => {
        file.value = e.target.files[0];
        if (valid.value) {
          emit("update:modelValue", reader.result);
          emit("change", file.value, type.value);
        } else {
          emit("change", null);
        }
      };
    };

    const isImage = computed(() => file.value?.type?.startsWith("image"));
    const tooltip = computed(
      () =>
        `Permitted file formats are ${accept.value
        }. Maximum file size is ${humanFileSize(mediaLimit.value)}`
    );

    return {
      handleInputFile,
      file,
      isImage,
      mediaLimit,
      humanFileSize,
      accept,
      valid,
      tooltip,
    };
  },
};
</script>

<style>
</style>