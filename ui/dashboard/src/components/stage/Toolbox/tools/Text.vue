<template>
  <section
    v-show="isWriting"
    class="writing"
    @click="onClickWriting"
    :style="{
      width: stageSize.width + 'px',
      height: stageSize.height + 'px',
      top: stageSize.top + 'px',
      left: stageSize.left + 'px',
    }"
  >
    <p ref="el" :style="options" contenteditable="true">
      Write or paste
      <br />your text here
    </p>
  </section>
  <template v-if="!isWriting">
    <div @click="createText" class="text-tool">
      <div class="icon is-large">
        <Icon size="36" src="new.svg" />
      </div>
      <span class="tag is-block">New</span>
    </div>
    <div v-for="text in savedTexts" :key="text" class="is-pulled-left">
      <Skeleton :data="text" />
    </div>
  </template>
  <template v-else>
    <div class="text-tool" style="width: 200px; z-index: 1005">
      <span class="tag muted is-block">Font</span>
      <Dropdown
        class="font-dropdown"
        v-model="options.fontFamily"
        :data="fontFamilies"
        @open="fontDropdownOpen"
      >
        <template #option="{ label }">
          <span :style="{ 'font-family': label }">{{ label }}</span>
        </template>
      </Dropdown>
    </div>
    <div class="text-tool" style="z-index: 1004">
      <span class="tag muted is-block">Size (px)</span>
      <Field
        :modelValue="options.fontSize.slice(0, -2)"
        @update:modelValue="changeFontSize"
        type="number"
      />
    </div>
    <div class="text-tool" style="z-index: 1003">
      <span class="tag muted is-block">Color</span>
      <ColorPicker v-model="options.color" />
    </div>
    <div class="text-tool" :class="{ active: options.fontWeight }" @click="toggleBold">
      <div class="icon is-large">
        <Icon size="36" src="bold.svg" />
      </div>
      <span class="tag is-block">Bold</span>
    </div>
    <div class="text-tool" :class="{ active: options.fontStyle }" @click="toggleItalic">
      <div class="icon is-large">
        <Icon size="36" src="italic.svg" />
      </div>
      <span class="tag is-block">Italic</span>
    </div>
    <div class="text-tool" :class="{ active: options.textDecoration }" @click="toggleUnderline">
      <div class="icon is-large">
        <Icon size="36" src="underline.svg" />
      </div>
      <span class="tag is-block">Underline</span>
    </div>
    <div class="text-tool has-tooltip-bottom" @click="saveText">
      <div class="icon is-large">
        <Icon size="40" src="check.svg" />
      </div>
      <span class="tag is-block">Save</span>
    </div>
    <div class="text-tool" @click="cancelWriting">
      <div class="icon is-large">
        <Icon size="32" src="cancel.svg" />
      </div>
      <span class="tag is-block">Cancel</span>
    </div>
  </template>
</template>

<script>
import Dropdown from "@/components/form/Dropdown";
import Field from "@/components/form/Field";
import ColorPicker from "@/components/form/ColorPicker";
import Skeleton from "../Skeleton";
import Icon from "@/components/Icon";
import { useStore } from "vuex";
import { computed, onUnmounted, ref } from "vue";

export default {
  components: { Dropdown, Field, ColorPicker, Skeleton, Icon },
  setup: () => {
    const store = useStore();
    const stageSize = computed(() => store.getters["stage/stageSize"]);
    const isWriting = computed(() => store.state.stage.preferences.isWriting);
    const options = store.state.stage.preferences.text;
    const fontFamilies = [
      "Josefin Sans",
      "Arial",
      "Times New Roman",
      "Helvetica",
      "Times",
      "Courier New",
      "Verdana",
      "Courier",
      "Arial Narrow",
      "Candara",
      "Geneva",
      "Calibri",
      "Optima",
      "Cambria",
      "Garamond",
      "Perpetua",
      "Monaco",
      "Didot",
      "Brush Script MT",
      "Lucida Bright",
      "Copperplate",
      "Roboto", // Opensource fonts
      "Open Sans",
      "Lato",
      "Roboto Condensed",
      "Oswald",
      "Poppins",
      "Roboto Mono",
      "PT Sans",
      "Ubuntu",
      "Playfair Display",
      "PT Serif",
      "Fira Sans",
      "Bebas Neue",
      "Anton",
      "Lobster",
      "Varela Round",
      "Arvo",
      "Pacifico",
      "Asap",
      "Overpass",
      "Abril Fatface",
    ];
    const changeFontSize = (value) => {
      options.fontSize = value.replace(/^\D+/g, "") + "px";
    };

    const createText = () => {
      store.commit("stage/UPDATE_IS_WRITING", true);
      store.commit("stage/SET_ACTIVE_MOVABLE", null);
      onClickWriting({
        clientX: window.innerWidth / 2 - 200,
        clientY: window.innerHeight / 2 - 50,
      });
    };

    const cancelWriting = () => {
      store.commit("stage/UPDATE_IS_WRITING", false);
    };

    const el = ref();
    const onClickWriting = (e) => {
      const { width, height } = el.value.getBoundingClientRect() ?? {};
      const x = e.clientX - stageSize.value.left - width / 2;
      const y = e.clientY - stageSize.value.top - height / 2;
      store.commit("stage/UPDATE_TEXT_OPTIONS", {
        left: x + "px",
        top: y + "px",
        x,
        y,
      });
      el.value.focus();
    };

    const saveText = async () => {
      const { width, height } = el.value.getBoundingClientRect() ?? {};
      store.commit("stage/UPDATE_IS_WRITING", false);
      store.dispatch("stage/addText", {
        ...options,
        content: el.value.innerHTML,
        w: width + 10,
        h: height + 10,
      });
    };

    const toggleBold = () => {
      let fontWeight;
      if (!options.fontWeight) {
        fontWeight = "bold";
      }
      store.commit("stage/UPDATE_TEXT_OPTIONS", { fontWeight });
    };

    const toggleItalic = () => {
      let fontStyle;
      if (!options.fontStyle) {
        fontStyle = "italic";
      }
      store.commit("stage/UPDATE_TEXT_OPTIONS", { fontStyle });
    };

    const toggleUnderline = () => {
      let textDecoration;
      if (!options.textDecoration) {
        textDecoration = "underline";
      }
      store.commit("stage/UPDATE_TEXT_OPTIONS", { textDecoration });
    };

    const savedTexts = computed(() => store.state.stage.board.texts);
    const fontDropdownOpen = (visible) => {
      document.querySelector("#topbar").style.overflow = visible
        ? "visible"
        : "auto";
    };
    onUnmounted(() => {
      document.querySelector("#topbar").style.overflow = "auto";
    })

    return {
      stageSize,
      options,
      fontFamilies,
      createText,
      isWriting,
      cancelWriting,
      onClickWriting,
      saveText,
      el,
      toggleBold,
      toggleItalic,
      toggleUnderline,
      changeFontSize,
      savedTexts,
      fontDropdownOpen,
    };
  },
};
</script>

<style lang="scss">
.writing {
  position: fixed;
  z-index: 1000;
  background-color: rgba($color: white, $alpha: 0.8);
  > p {
    position: absolute;
  }
}
.text-tool {
  z-index: 1001;
  position: relative;
  float: left;
}
</style>