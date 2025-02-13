<template>
    <div v-if="objects.find(el => el.type == 'jitsi')" id="reload-stream">
        <a-tooltip title="Reload streams">
            <button class="button is-small refresh-icon clickable" @mousedown="onReload">
                <i class="fas fa-sync"></i>
            </button>
        </a-tooltip>
    </div>
</template>

<script>
import { useStore } from "vuex";
import { computed } from "vue";

export default {
    components: {},
    setup: () => {
        const store = useStore();
        const objects = computed(() => store.getters["stage/objects"]);
        const onReload = () => store.dispatch("stage/reloadStreams");
        return {
            objects,
            onReload
        };
    },
};
</script>

<style scoped lang="scss">
#reload-stream {
    position: fixed;
    right: 12px;
    top: 85px;
    width: 180px;
    text-align: center;
    z-index: 4;

    @media screen and (max-width: 767px) {
        right: unset;
        top: 8px;
        left: 0;
    }
}

.refresh-icon {
    width: 20px;
    height: 20px;
    padding: 0px;

    &:hover {
        transform: scale(1.2);
    }
}
</style>