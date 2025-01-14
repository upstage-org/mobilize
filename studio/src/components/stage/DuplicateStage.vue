<template>
  <CustomConfirm @confirm="(complete) => duplicateStage(complete)" :loading="loading">
    <Field v-model="name" label="Enter new stage name" :placeholder="defaultName" />
    <template #trigger>
      <slot></slot>
    </template>

    <template #no>
      <span class="icon">
        <i class="fas fa-times"></i>
      </span>
      <span>{{ $t("cancel") }}</span>
    </template>
    <template #yes>
      <span class="icon">
        <i class="fas fa-clone"></i>
      </span>
      <span>{{ $t("duplicate") }}</span>
    </template>
  </CustomConfirm>
</template>

<script setup>
import { defineProps, computed, inject, ref } from "vue";
import CustomConfirm from "components/CustomConfirm.vue";
import Field from "components/form/Field.vue";
import { useMutation } from "services/graphql/composable";
import { stageGraph } from "services/graphql";
import { useRouter } from "vue-router";

const props = defineProps({
  stage: Object
});

const router = useRouter();
const name = ref("");
const defaultName = computed(() => `A clone of ${props.stage.name}`);
const refresh = inject("refresh");
const ClearCache = inject("afterDuplicate");
const { loading, save } = useMutation(stageGraph.duplicateStage);
const duplicateStage = async (complete) => {
  const payload = {
    id: props.stage.id,
    name: name.value || defaultName.value,
  };
  const result = await save(
    `${payload.name} was duplicated successfully!`,
    payload,
  );
  complete();
  ClearCache();
  refresh();
  router.push(
    `/stages/stage-management/${result.duplicateStage.id}/`,
  );
  console.log(result);
};
</script>

<style></style>
