<template>
  <div
    v-for="stream in streams"
    :key="stream"
  >
    <Skeleton :data="stream">
      <video :src="stream.url"></video>
    </Skeleton>
  </div>
</template>

<script>
import { computed, onMounted } from "vue";
import { useStore } from "vuex";
import Skeleton from "../../Skeleton.vue";
import Icon from "components/Icon.vue";
import Loading from "components/Loading.vue";

export default {
  components: {
    Skeleton,
    Icon,
    Loading,
  },
  setup: () => {
    const store = useStore();

    const streams = computed(() => {
      const res = [...store.state.stage.tools.streams];
      return res;
    });

    return { streams };
  },
};
</script>

<style lang="scss" scoped>
@mixin gradientText($from, $to) {
    background: linear-gradient(to top, $from, $to);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.fas.fa-plus {
  @include gradientText(#30ac45, #6fb1fc);
}

video {
  height: 100%;
}

.centered {
  margin: auto;
}

.pending-stream {
  cursor: not-allowed;
}
</style>
