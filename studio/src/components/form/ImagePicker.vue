<template>
  <modal>
    <template #trigger>
      <Asset class="clickable" v-if="modelValue" :asset="{
        src: modelValue,
      }" />
      <button v-else class="button">{{ $t("choose_an_image") }}</button>
    </template>
    <template #header><span>{{
        $t("choose_an_existing_image_or_upload_new")
      }}</span></template>
    <template #content="{ closeModal }">
      <Loading v-if="loading" />
      <div v-else class="columns is-multiline">
        <div class="column is-12">
          <div class="columns">
            <div class="column uploadbtn">
              <MediaUpload />
            </div>

            <div class="column">
              <p class="control has-icons-left">
                <input class="input" type="text" placeholder="Search Media" v-model="filter.name" />
                <span class="icon is-left">
                  <i class="fas fa-search" aria-hidden="true"></i>
                </span>
              </p>
            </div>
            <Dropdown class="column" v-model="filter.mediaType" :data="types" :render-label="(type) => (type.name === 'media' ? 'All types' : type.name)
        " :render-value="(type) => type" style="width: 100%" fixed placeholder="All Types" />
            <Dropdown class="column" v-model="filter.owner" :data="users" :render-label="(user) => displayName(user)"
              :render-value="(user) => user" style="width: 100%" fixed placeholder="All Users" />
            <Dropdown class="column" v-model="filter.stage" :data="stages" :render-label="(stage) => stage.name"
              :render-value="(stage) => stage" style="width: 100%" fixed placeholder="All Stages" />
          </div>
        </div>
        <div class="column is-12 gallery">
          <div v-for="item in availableImages" :key="item">
            <div class="card-image clickable" @click="select(item, closeModal)">
              <Asset :asset="item" />
            </div>
          </div>
        </div>
      </div>
    </template>
  </modal>
</template>

<script>
import Modal from "components/Modal.vue";
import Loading from "components/Loading.vue";
import Asset from "components/Asset.vue";
import { computed, provide, reactive, onMounted } from "vue";
import Dropdown from "./Dropdown.vue";
import { displayName } from "utils/common";
import { stageGraph } from "services/graphql";
import { useQuery } from "services/graphql/composable";
import MediaUpload from "./Media/MediaUpload.vue";

export default {
  props: ["modelValue"],
  emits: ["update:modelValue"],
  components: { Modal, Loading, Asset, Dropdown, MediaUpload },
  setup: (props, { emit }) => {
    const {
      loading,
      nodes: mediaList,
      refresh,
    } = useQuery(stageGraph.mediaList);
    const type_dis = ["avatar", "prop", "backdrop", "shape", "curtain"];
    provide("refresh", refresh);

    onMounted(() => {
      refresh();
    });

    const select = (item, closeModal) => {
      emit("update:modelValue", item.src);
      closeModal();
    };

    const filter = reactive({
      name: null,
      mediaType: null,
      owner: null,
      stage: null,
    });

    const { nodes: typesData } = useQuery(stageGraph.mediaTypeList);
    const types = computed(() => {
      const list = [];
      list.push({ id: null, name: "All Types" });
      typesData.value
        .filter((m) => type_dis.includes(m.name))
        .forEach((type) => list.push(type));
      return list;
    });

    const users = computed(() => {
      let list = [];
      list.push({ id: null, displayName: "All Users" });
      if (mediaList.value) {
        mediaList.value.forEach(({ owner }) => {
          if (!list.some((user) => user.username === owner.username)) {
            list.push(owner);
          }
        });
      }
      return list;
    });

    const { nodes: stagesData } = useQuery(stageGraph.stageList);
    const stages = computed(() => {
      let list = [];
      list.push({ id: null, name: "All Stages" });
      if (stagesData.value) {
        stagesData.value.forEach((stage) => list.push(stage));
      }
      return list;
    });

    const availableImages = computed(() => {
      let list = mediaList.value;
      list = list.filter((m) => type_dis.includes(m.assetType.name));
      if (filter.name) {
        list = list.filter((media) =>
          media.name.toLowerCase().includes(filter.name.toLowerCase()),
        );
      }
      if (filter.assetType && filter.assetType.id) {
        list = list.filter(
          (media) => media.assetType.name === filter.assetType.name,
        );
      }
      if (filter.owner && filter.owner.id) {
        list = list.filter(
          (media) => media.owner.username === filter.owner.username,
        );
      }
      if (filter.stage && filter.stage.id) {
        list = list.filter((media) =>
          media.stages.find((s) => s.id === filter.stage.dbId),
        );
      }
      return list;
    });

    return {
      loading,
      availableImages,
      select,
      filter,
      types,
      users,
      displayName,
      stages,
    };
  },
};
</script>

<style>
.modal-card-title {
  margin-bottom: 0px;
}

.modal-card {
  border-top: none;
}

.dropdown .button {
  width: 95%;
}

.dropdown-content {
  margin-left: 1%;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-gap: 1.5rem;
}

.gallery .card-image {
  display: flex;
  justify-content: center;
}

.gallery img {
  height: 10vw;
  width: auto;
}

.uploadbtn {
  flex-grow: 0;
}
</style>
