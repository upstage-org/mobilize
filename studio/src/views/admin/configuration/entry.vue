<script setup lang="ts">
import { useLoading } from "hooks/mutations";
import { VNode } from "vue";
import { ref } from "vue";
import RichTextEditor from "components/editor/RichTextEditor.vue";
import { boxShadow } from "html2canvas/dist/types/css/property-descriptors/box-shadow";
import { configGraph } from 'services/graphql';

const props = defineProps<{
  name: string;
  label: string;
  defaultValue: string | boolean;
  multiline?: boolean;
  richTextEditor?: boolean;
  help?: VNode;
  refresh?: () => Promise<void>;
}>();

const editing = ref(false);
const value = ref(props.defaultValue);

const { loading, proceed } = useLoading(async () => configGraph.saveConfig(props.name, !value.value ? "" : String(value.value)));

const save = async () => {
  editing.value = false;
  await proceed();
  if (props.refresh) {
    await props.refresh();
  }
};
</script>

<template>
  <a-form-item :label="props.label" :name="name" :label-col="{ span: 12, xl: { span: 4 }, xxl: { span: 3 } }">
    <template v-if="typeof value === 'string'">
      <a-input-group compact style="display: flex">
        <RichTextEditor v-if="richTextEditor" :readonly="!editing" v-model="value" :style="{
          boxShadow: 'none',
          pointerEvents: editing ? 'auto' : 'none'
        }" />
        <template v-else>
          <a-textarea v-if="props.multiline" :disabled="!editing" v-model:value="value" style="color: black"
            auto-size></a-textarea>
          <a-input v-else :disabled="!editing" v-model:value="value" style="color: black" />
        </template>
        <a-button v-if="!editing && !loading" type="primary" @click="editing = true">Edit</a-button>
        <a-button v-else type="primary" @click="save" :loading="loading">Save</a-button>
      </a-input-group>
    </template>
    <a-switch v-if="typeof value === 'boolean'" v-model:checked="value" @change="save" :loading="loading" />
    <help v-if="help" class="mt-2" />
  </a-form-item>
</template>
<style>
.richtexteditor {}
</style>