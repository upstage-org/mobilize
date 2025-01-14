<template>
  <div class="card-header">
    <span class="card-header-title">{{ $t("create_new_meeting_room") }}</span>
  </div>
  <div class="card-content voice-parameters">
    <form @submit.prevent="createRoom">
      <HorizontalField title="Room name">
        <Field
          v-model="form.name"
          required
          required-message="Room name is required"
          pattern="^[^?&:&quot;'%#]+$"
          title="Meeting name should not contain any of these characters: ?, &, :, ', &quot;, %, #."
        >
        </Field>
      </HorizontalField>
      <SaveButton :disabled="!form.name.trim()">{{
        $t("create_room")
      }}</SaveButton>
    </form>
  </div>
</template>

<script>
import Field from "components/form/Field.vue";
import SaveButton from "components/form/SaveButton.vue";
import { useStore } from "vuex";
import { reactive, computed } from "vue";
import HorizontalField from "components/form/HorizontalField.vue";
export default {
  components: { Field, SaveButton, HorizontalField },
  emits: ["close"],
  setup: (_, { emit }) => {
    const store = useStore();
    const stageSize = computed(() => store.getters["stage/stageSize"]);

    const form = reactive({ name: "" });
    const createRoom = async () => {
      store.commit("stage/CREATE_ROOM", {
        type: "meeting",
        name: form.name,
        description: "",
        w: stageSize.value.width / 2,
        h: stageSize.value.height / 2,
      });
      emit("close");
    };

    return { form, createRoom };
  },
};
</script>

<style></style>
