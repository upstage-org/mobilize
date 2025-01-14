<template>
  <div>
    <Object :object="meeting">
      <template #render>
        <div
          id="meeting-room"
          class="frame"
          :style="{ width: object.w + 'px', height: object.h + 'px' }"
          :class="activeMovable ? 'disable-pointer' : ''"
        >
          <Loading v-if="loading" height="100%" />
          <div class="room" ref="room"></div>
        </div>
      </template>
    </Object>
  </div>
</template>

<script>
import Object from "../Object.vue";
import Loading from "components/Loading.vue";
import { computed, onMounted, ref } from "vue";
import { useStore } from "vuex";
import { useJitsiDomain } from "./composable";

export default {
  components: { Object, Loading },
  props: ["object"],
  setup: (props) => {
    const store = useStore();
    const room = ref();
    const meeting = computed(() => props.object);

    onMounted(() => {
      const domain = useJitsiDomain();
      const options = {
        roomName: props.object.name,
        subject: "Powered by Jitsi",
        width: "100%",
        height: "100%",
        parentNode: room.value,
        userInfo: {
          email: store.state.user.user?.email,
          displayName: store.getters["user/chatname"],
        },
        configOverwrite: {
          prejoinPageEnabled: false,
          startVideoMuted: 1,
          startAudioMuted: 1,
        },
        interfaceConfigOverwrite: { SHOW_CHROME_EXTENSION_BANNER: false },
        disableInitialGUM: true,
      };
      const api = new window.JitsiMeetExternalAPI(domain, options);
      console.log(api);
    });

    const activeMovable = computed(() => store.getters["stage/activeMovable"]);

    return { meeting, room, activeMovable };
  },
};
</script>

<style lang="scss" scoped>

.frame {
  border: 2px solid black;
  border-top: 10px solid #007011;
  border-radius: 8px;
  box-sizing: border-box;
  overflow: hidden;

  .room {
    height: 100%;
  }
}

.disable-pointer {
  pointer-events: none;
}
</style>
