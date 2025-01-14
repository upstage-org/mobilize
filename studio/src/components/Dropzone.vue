<script setup lang="ts">
import { ref, provide } from "vue";
import configs from "config";
import { StudioGraph, UploadFile } from "models/studio";
import { message } from "ant-design-vue";
import { useLazyQuery } from "@vue/apollo-composable";
import gql from "graphql-tag";
import { uploadDefault } from "models/studio";
import i18n from "../i18n";
import { humanFileSize } from "utils/common";

const { load, refetch } = useLazyQuery<StudioGraph>(
  gql`
    query WhoAmI {
      whoami {
        uploadLimit
      }
    }
  `,
  {},
  {
    fetchPolicy: "network-only",
  },
);

const visible = ref(false);
const files = ref<UploadFile[]>([]);
const composingMode = ref(false);
provide("composingMode", composingMode);
provide("files", files);
provide("visibleDropzone", visible);

window.addEventListener("dragenter", (e) => {
  e.preventDefault();
  visible.value = true;
});

const toSrc = ({ file }: { file: File }) => {
  return URL.createObjectURL(file);
};

const handleUpload = async (file: UploadFile) => {
  let fileType = file.file.type;
  const profile = (await (load as any)()) || (await refetch());
  const uploadLimit = (profile?.data || profile?.whoami).uploadLimit ?? uploadDefault;

  if (!fileType.includes("video")) {
    const canUpload = file.file.size <= uploadLimit;
    if (!canUpload) {
      const hide = message.error({
        content: i18n.global.t("over_limit_upload", {
          size: humanFileSize(file.file.size),
          limit: humanFileSize(profile?.data.whoami.uploadLimit ?? 0),
          name: file.file.name,
        }),
        duration: 0,
        onClick: () => hide(),
        class: "cursor-pointer",
      });
      return;
    }
  }

  files.value = files.value.concat({
    ...file,
    id: files.value.length,
    preview: toSrc(file),
    status: "local",
  });
};

const uploadFile = async (file: any) => {
  await handleUpload(file);
  visible.value = false;
};
</script>

<template>
  <a-modal :footer="null" :visible="visible" @cancel="visible = false" width="100%" wrapClassName="fullscreen-dragzone"
    class="h-full top-0 p-0">
    <a-upload-dragger :show-upload-list="false" :custom-request="uploadFile" multiple>
      <p class="ant-upload-drag-icon">
        <UploadOutlined />
      </p>
      <p class="ant-upload-text">{{ $t("upload_hint") }}</p>
      <p class="ant-upload-hint">
        {{
          $t("upload_accepted_format", {
            image: configs.ALLOWED_EXTENSIONS.IMAGE,
            audio: configs.ALLOWED_EXTENSIONS.AUDIO,
            video: configs.ALLOWED_EXTENSIONS.VIDEO,
          })
        }}
      </p>
    </a-upload-dragger>
  </a-modal>
  <slot></slot>
</template>

<style lang="less">
.fullscreen-dragzone {
  z-index: 999999;

  .ant-modal {
    max-width: unset;

    .ant-modal-content {
      height: 100%;
      padding-right: 48px;
    }

    .ant-modal-body {
      padding: 0;
      height: 100%;
    }

    .ant-upload-btn {
      display: flex !important;
      flex-direction: column;
      justify-content: center;
    }
  }
}
</style>
