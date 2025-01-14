<template>
  <div class="columns">
    <template v-for="(column, i) in columns" :key="column">
      <div class="column">
        <article class="panel is-light">
          <p class="panel-heading">
            {{ column }}
            <span class="tag is-primary">
              {{ i == columns.length - 1 ? count(i) + 1 : count(i) }}
            </span>
          </p>
          <div class="panel-heading pt-0">
            <p class="control has-icons-left">
              <input
                class="input is-primary"
                type="text"
                placeholder="Search"
                v-model="searchs[i]"
              />
              <span class="icon is-left">
                <i class="fas fa-search" aria-hidden="true"></i>
              </span>
            </p>
          </div>
          <div class="panel-body">
            <a v-if="i == columns.length - 1" class="panel-block owner">
              {{ renderLabel(owner) }}
              <p class="panel-tag">owner</p>
            </a>
            <template v-for="(item, j) in data" :key="renderValue(item)">
              <a
                v-if="shouldVisible(j, i)"
                class="panel-block"
                @click="moveRight(j)"
                @contextmenu.prevent="moveLeft(j)"
              >
                {{ renderLabel(item) }}
              </a>
            </template>
          </div>
        </article>
      </div>
      <div class="column is-narrow px-0" v-if="i < columns.length - 1">
        <button class="button is-primary is-small" @click="moveAll(i, i + 1)">
          <i class="fas fa-angle-double-right"></i>
        </button>
        <br />
        <br />
        <button class="button is-primary is-small" @click="moveAll(i + 1, i)">
          <i class="fas fa-angle-double-left"></i>
        </button>
      </div>
    </template>
  </div>
</template>

<script>
import { reactive } from "vue";
import { watch } from "vue";
import { includesIgnoreCase } from "utils/common";
export default {
  props: {
    columns: Array,
    modelValue: Array,
    data: { type: Array, default: () => [] },
    owner: Object,
    renderLabel: {
      type: Function,
      default: (item) => item,
    },
    renderValue: {
      type: Function,
      default: (item) => item,
    },
    renderKeywords: Function,
  },
  emits: ["update:modelValue"],
  setup: (props, { emit }) => {
    const positions = reactive([]);
    const searchs = reactive([]);

    const matchSearch = (item, column) => {
      if (!searchs[column]) {
        return true;
      }
      const transform = props.renderKeywords ?? props.renderLabel;
      return includesIgnoreCase(transform(props.data[item]), searchs[column]);
    };

    const shouldVisible = (item, column) => {
      return (positions[item] ?? 0) === column && matchSearch(item, column);
    };

    const moveRight = (item) => {
      let currentPosition = positions[item] ?? 0;
      if (currentPosition < props.columns.length - 1) {
        positions[item] = currentPosition + 1;
      }
    };

    const moveLeft = (item) => {
      positions[item] = (positions[item] ?? 1) - 1;
    };

    watch(positions, () => {
      let res = [];
      for (let i = 1; i < props.columns.length; i++) {
        if (!res[i - 1]) {
          res[i - 1] = [];
        }
        for (let j = 0; j < props.data.length; j++) {
          if (positions[j] === i) {
            res[i - 1].push(props.renderValue(props.data[j]));
          }
        }
      }
      emit("update:modelValue", res);
    });

    watch(
      [() => props.modelValue, () => props.data],
      ([val]) => {
        if (props.data) {
          for (let i = 0; i < val.length; i++) {
            for (let j = 0; j < (val[i] ?? []).length; j++) {
              positions[
                props.data.findIndex(
                  (item) => props.renderValue(item) === val[i][j],
                )
              ] = i + 1;
            }
          }
        }
      },
      { immediate: true },
    );

    const count = (i) =>
      props.data
        ? props.data.filter((item, p) => (positions[p] ?? 0) === i).length
        : 0;

    const moveAll = (from, to) => {
      for (let i = 0; i < props.data.length; i++) {
        if ((positions[i] ?? 0) === from && shouldVisible(i, from)) {
          positions[i] = to;
        }
      }
    };

    return { shouldVisible, moveRight, moveLeft, count, searchs, moveAll };
  },
};
</script>

<style scoped>
article.panel {
  width: 100%;
}
.panel-heading {
  font-size: unset;
}
.panel-body {
  max-height: 50vh;
  overflow-y: auto !important;
}
.panel-block.owner {
  position: relative;
  background-color: #00000015;
}
.panel-tag {
  position: absolute;
  background-color: #007011;
  font-size: 0.8rem;
  color: #fff;
  padding: 0 5px;
  right: 10px;
}
</style>
