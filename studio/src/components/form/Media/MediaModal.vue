<template>
  <section class="modal-card-body p-0">
    <button class="delete close-modal" aria-label="close" @click="closeModal"></button>
    <div class="container-fluid">
      <footer class="modal-card-foot">
        <div class="columns is-fullwidth">
          <div class="column is-narrow">
            <SaveButton @click="save" :loading="loading" :disabled="!form.name || !form.mediaType" />
          </div>
          <div class="column is-narrow">
            <Field horizontal label="Media Type">
              <MediaType v-model="form.mediaType" :data="availableTypes" />
            </Field>
          </div>
          <div class="column">
            <Field horizontal v-model="form.name" label="Media Name" />
          </div>
        </div>
      </footer>
      <Tabs :items="tabs">
        <template #extras>
          <Upload v-model="form.base64" :type="fileType" :preview="false">
            <span class="icon">
              <i class="fas fa-retweet"></i>
            </span>
            <span>{{ $t("replace") }}</span>
          </Upload>
        </template>
        <template #preview>
          <div class="preview">
            <template>
              <Asset :asset="media" @detect-size="updateMediaSize" />
            </template>
          </div>
        </template>
        <template #copyright>
          <HorizontalField title="Copyright Level">
            <Dropdown v-model="form.copyrightLevel" :data="copyrightLevels" :render-label="(item) => item.name"
              :render-value="(item) => item.value" :render-description="(item) => item.description" />
          </HorizontalField>
          <HorizontalField v-show="[2].includes(form.copyrightLevel)">
            <div style="margin-right: 32px">
              <MultiTransferColumn :columns="['No access', 'Readonly access', 'Editor access']" :data="users"
                :renderLabel="displayName" :renderValue="(item) => item.dbId" :renderKeywords="(item) =>
      `${item.firstName} ${item.lastName} ${item.username} ${item.email} ${item.displayName}`
      " v-model="playerAccess" />
            </div>
          </HorizontalField>
        </template>
        <template #stages>
          <MultiSelectList :loading="loadingAllStages" :data="availableStages" v-model="form.assignedStages"
            :columnClass="() => 'is-12 p-0'">
            <template #render="{ item }">
              <div class="box m-0 p-2">
                <div class="content">
                  <strong>{{ item.name }}</strong>
                  <span style="float: right">
                    Created by
                    <span class="has-text-primary">{{
      displayName(item.owner)
    }}</span>
                  </span>
                </div>
              </div>
            </template>
          </MultiSelectList>
        </template>
        <template #voice>
          <VoiceParameters v-model="form.voice" />
        </template>
        <template #link>
          <HorizontalField title="URL">
            <Field placeholder="The destination when audience click on the link" v-model="form.link.url" />
          </HorizontalField>
          <HorizontalField title="Open in new tab">
            <Switch v-model="form.link.blank" />
          </HorizontalField>
        </template>
        <template #multiframe>
          <Multiframe :media="media" :form="form" />
        </template>
      </Tabs>
    </div>
  </section>
</template>

<script>
import { reactive, ref } from "@vue/reactivity";
import { useMutation, useQuery } from "services/graphql/composable";
import { stageGraph, userGraph } from "services/graphql";
import { computed, inject, watch } from "@vue/runtime-core";
import { message } from "ant-design-vue";
import HorizontalField from "components/form/HorizontalField.vue";
import Field from "components/form/Field.vue";
import MediaType from "components/form/MediaType.vue";
import SaveButton from "components/form/SaveButton.vue";
import Upload from "components/form/Upload.vue";
import Dropdown from "components/form/Dropdown.vue";
import Asset from "components/Asset.vue";
import MultiSelectList from "components/MultiSelectList.vue";
import Tabs from "components/Tabs.vue";
import MultiTransferColumn from "components/MultiTransferAccessColumn.vue";
import VoiceParameters from "components/stage/SettingPopup/settings/VoiceParameters.vue";
import { displayName } from "utils/auth";
import { MEDIA_COPYRIGHT_LEVELS } from "utils/constants";
import Multiframe from "./Multiframe.vue";
import Switch from "components/form/Switch.vue";

export default {
  components: {
    HorizontalField,
    Field,
    MediaType,
    SaveButton,
    Asset,
    MultiSelectList,
    Tabs,
    VoiceParameters,
    Upload,
    MultiTransferColumn,
    Dropdown,
    Multiframe,
    Switch,
  },
  props: {
    media: Object,
  },
  emits: ["complete"],
  setup: (props, { emit }) => {
    const form = reactive(props.media);
    form.multi = false;
    form.frames = [];
    form.voice = {};
    if (form.description) {
      Object.assign(form, JSON.parse(form.description));
    }
    if (!form.link) {
      form.link = {
        blank: true,
      };
    }
    if (form.assetType) {
      form.assetType = form.assetType.name;
    }

    const { mutation: uploadMedia } = useMutation(stageGraph.uploadMedia);
    const { mutation: updateMedia } = useMutation(stageGraph.updateMedia);
    const { mutation: assignStages } = useMutation(stageGraph.assignStages);

    const loading = ref(false);
    const save = async () => {
      try {
        loading.value = true;
        const {
          name,
          base64,
          mediaType,
          filename,
          copyrightLevel,
          playerAccess,
        } = form;
        let msg = "Media updated successfully!";
        if (!form.id) {
          const response = await uploadMedia({
              name,
              base64,
              mediaType,
              filename,
            });
            Object.assign(form, response.uploadMedia.asset);
          msg = "Media created successfully!";
        }
        const stageIds = form.assignedStages.map((s) => s.dbId);
        const {
          id,
          multi,
          frames,
          voice,
          link,
          src,
          w,
          h,
          uploadedFrames,
        } = form;
        const payload = {
          id,
          name,
          mediaType,
          base64,
          description: JSON.stringify({
            multi,
            frames,
            voice,
            link,
            w,
            h,
          }),
          fileLocation: src,
          copyrightLevel,
          playerAccess,
          uploadedFrames,
        };
        await Promise.all([updateMedia(payload), assignStages(id, stageIds)]);
        //message.success(msg);
        emit("complete", form);
        closeModal();
      } catch (error) {
        //message.error(error);
        closeModal();
      } finally {
        loading.value = false;
      }
    };

    const fileType = computed(() => {
      if (["avatar", "prop", "backdrop", "curtain"].includes(form.mediaType)) {
        return "image";
      }
      if (["audio"].includes(form.mediaType)) {
        return "audio";
      }
      if (["stream"].includes(form.mediaType)) {
        return "video";
      }
    });
    const availableTypes = computed(() => {
      const type = form.fileType ?? fileType.value;
      if (type === "image") return ["avatar", "prop", "backdrop", "curtain"];
      if (type === "audio") return ["audio"];
      if (type === "video") return ["stream"];
    });

    const tabs = computed(() => {
      const res = [
        { key: "preview", label: "Preview", icon: "fas fa-image" },
        { key: "copyright", label: "Copyright", icon: "fas fa-copyright" },
        { key: "stages", label: "Stage", icon: "fas fa-person-booth" },
      ];
      if (form.mediaType === "avatar") {
        res.push({ key: "voice", label: "Voice", icon: "fas fa-volume-up" });
      }
      if (["avatar", "prop"].includes(form.mediaType)) {
        res.push({ key: "link", label: "Link", icon: "fas fa-link" });
      }
      if (["avatar", "prop", "backdrop"].includes(form.mediaType)) {
        res.push({
          key: "multiframe",
          label: "Multiframe",
          icon: "fas fa-clone",
        });
      }
      return res;
    });
    const { nodes: stageList, loading: loadingAllStages } = useQuery(
      stageGraph.stageList,
    );
    const availableStages = computed(() => {
      if (!stageList.value) return [];
      const res = stageList.value.filter(
        (stage) =>
          stage.permission === "owner" || stage.permission === "editor",
      );
      res.sort((a, b) => (a.name > b.name ? 1 : -1));
      return res;
    });
    watch(
      stageList,
      (val) => {
        if (val) {
          form.assignedStages = form.stages.map((stage) =>
            val.find((s) => s.dbId === stage.id),
          );
        } else {
          form.assignedStages = [];
        }
      },
      { immediate: true },
    );

    const closeModal = inject("closeModal");

    const updateMediaSize = ({ width, height }) => {
      if (width > height) {
        form.w = 100;
        form.h = (100 * height) / width;
      } else {
        form.h = 100;
        form.w = (100 * width) / height;
      }
    };

    const copyrightLevels = MEDIA_COPYRIGHT_LEVELS;
    const { nodes: users } = useQuery(userGraph.userList);
    const playerAccess = ref(
      form.playerAccess ? JSON.parse(form.playerAccess) : [],
    );
    watch(playerAccess, (val) => {
      form.playerAccess = JSON.stringify(val);
    });

    return {
      form,
      loading,
      save,
      availableTypes,
      tabs,
      availableStages,
      displayName,
      closeModal,
      updateMediaSize,
      fileType,
      copyrightLevels,
      users,
      playerAccess,
      loadingAllStages,
    };
  },
};
</script>

<style lang="scss" scoped>
:deep(.field-label) {
  white-space: nowrap;
  margin: auto;
  margin-right: 10px;
}

:deep(.file) {
  justify-content: center;
}

:deep(.file-cta) {
  background-color: transparent;
  border-color: transparent;
}

:deep(.tab-content) {
  padding: 16px;
  padding-top: 0;
}

.close-modal {
  position: absolute;
  right: 20px;
  top: 10px;
  z-index: 20;
}

.modal-card-body {
  min-height: 325px;

  .modal-card-foot {
    padding-right: 24px;

    :deep(.field-label) {
      flex: none;
    }
  }
}

.preview {
  text-align: center;

  .field {
    text-align: left;
  }
}
</style>