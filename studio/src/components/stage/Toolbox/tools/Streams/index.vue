<template>
  <div
    v-for="stream in streams"
    :key="stream"
    :class="{ 'has-background-warning': !stream.ready && stream.alive }"
  >
    <Skeleton :data="stream" :nodrop="!stream.ready">
      <video :src="stream.url"></video>
    </Skeleton>
  </div>
  <!-- <div v-if="loading">
    <Loading height="64px" />
  </div>
  <div v-else @click="fetchRunningStreams">
    <div class="icon is-large">
      <Icon src="refresh.svg" size="36" />
    </div>
    <span class="tag is-light is-block">{{ $t("refresh") }}</span>
  </div> -->
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
    const runningStreams = computed(() => store.state.stage.runningStreams);
    const loading = computed(() => store.state.stage.loadingRunningStreams);

    const autoDetect = computed(
      () => store.state.stage.config.streaming?.autoDetect,
    );

    const streams = computed(() => {
      const res = [...store.state.stage.tools.streams];
      res.forEach((s) => (s.alive = false));
      runningStreams.value.forEach((stream) => {
        const index = res.findIndex((s) => s.url === stream.url);
        if (index >= 0) {
          res[index].alive = true;
          if (stream.w > 0 && stream.h > 0) {
            res[index].w = stream.w;
            res[index].h = stream.h;
          }
        } else {
          if (autoDetect.value) {
            res.push(stream);
          }
        }
      });
      console.log(res);
      return res;
    });

    const scanVideo = ({ width, height }, stream) => {
      console.log(stream, width, height);
      if (!stream.ready) {
        Object.assign(stream, {
          w: (100 * width) / height,
          h: 100,
          ready: true,
        });
      }
    };

    return { streams, loading, fetchRunningStreams, autoDetect, scanVideo };
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
