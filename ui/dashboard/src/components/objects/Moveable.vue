<template>
  <div
    ref="el"
    :style="{
      position: 'absolute',
      opacity: object.opacity * (isDragging ? 0.5 : 1),
      filter: `grayscale(${object.liveAction ? 0 : 1})`,
      'transform-origin': transformOrigin,
    }"
    @mousedown="clickInside"
    v-click-outside="clickOutside"
  >
    <slot />
  </div>
  <div
    v-if="isDragging"
    :style="{
      position: 'absolute',
      left: object.x + 'px',
      top: object.y + 'px',
      width: object.w + 'px',
      height: object.h + 'px',
      transform: `rotate(${object.rotate}deg)`,
      opacity: object.opacity,
      filter: `grayscale(${object.liveAction ? 0 : 1})`,
    }"
  >
    <slot />
  </div>
</template>

<script>
import { ref } from "@vue/reactivity";
import { computed, onMounted, onUnmounted, watch } from "@vue/runtime-core";
import Moveable from "moveable";
import { useStore } from "vuex";
import anime from "animejs";

export default {
  props: ["object", "controlable", "active"],
  emits: ["update:active"],
  setup: (props, { emit }) => {
    const el = ref();
    const isDragging = ref(false);

    const store = useStore();
    const config = store.getters["stage/config"];
    const moveable = new Moveable(document.body, {
      draggable: true,
      resizable: true,
      rotatable: true,
      origin: false,
    });

    let animation;

    const sendMovement = (target, { left, top }) => {
      target.style.left = `${props.object.x}px`;
      target.style.top = `${props.object.y}px`;
      store.dispatch("stage/shapeObject", {
        ...props.object,
        x: left,
        y: top,
      });
    };
    moveable
      .on("dragStart", () => {
        isDragging.value = true;
        if (animation) {
          animation.pause(true);
        }
      })
      .on("drag", ({ target, left, top }) => {
        target.style.left = `${left}px`;
        target.style.top = `${top}px`;
      })
      .on("dragEnd", ({ lastEvent, target }) => {
        if (lastEvent) {
          sendMovement(target, lastEvent);
        }
        isDragging.value = false;
      });

    const sendResize = (target, { width, height, left, top }) => {
      store.dispatch("stage/shapeObject", {
        ...props.object,
        x: left,
        y: top,
        w: width,
        h: height,
      });
    };
    moveable
      .on("resizeStart", () => {
        isDragging.value = true;
        if (animation) {
          animation.pause(true);
        }
      })
      .on("resize", ({ target, width, height, drag: { left, top } }) => {
        target.style.width = `${width}px`;
        target.style.height = `${height}px`;
        target.style.left = `${left}px`;
        target.style.top = `${top}px`;
      })
      .on(
        "resizeEnd",
        ({
          target,
          lastEvent: {
            width,
            height,
            drag: { left, top },
          },
        }) => {
          sendResize(target, { left, top, width, height });
          isDragging.value = false;
        }
      );

    const sendRotation = (target, rotate) => {
      target.style.transform = `rotate(${props.object.rotate}deg)`;
      store.dispatch("stage/shapeObject", {
        ...props.object,
        rotate,
      });
    };
    moveable
      .on("rotateStart", (e) => {
        e.set(props.object.rotate ?? 0);
        isDragging.value = true;
        if (animation) {
          animation.pause(true);
        }
      })
      .on("rotate", ({ target, rotate }) => {
        target.style.transform = `rotate(${rotate}deg)`;
      })
      .on("rotateEnd", ({ target, lastEvent: { rotate } }) => {
        sendRotation(target, rotate);
        isDragging.value = false;
      });

    const showControls = (isShowing, e) => {
      if (moveable) {
        if (isShowing) {
          moveable.setState(
            {
              target: el.value,
              keepRatio: props.object.type !== "text",
            },
            () => {
              if (e && props.object.type !== "text") {
                moveable.dragStart(e);
              }
            }
          );
          emit("update:active", true);
        } else {
          moveable.setState(
            {
              target: null,
            },
            () => {
              emit("update:active", false);
            }
          );
        }
      }
    };

    const activeMovable = computed(
      () => store.state.stage.activeMovable === props.object.id
    );

    const clickInside = (e) => {
      if (props.controlable) {
        showControls(true, e);
        store.commit("stage/SET_ACTIVE_MOVABLE", props.object.id);
      }
    };

    const clickOutside = (e) => {
      if ((!e || e.target.id === "board") && props.controlable) {
        store.commit("stage/SET_ACTIVE_MOVABLE", null);
      }
    };
    watch(
      activeMovable,
      (val) => {
        showControls(val);
      },
      { immediate: true }
    );

    watch(
      () => props.object,
      () => {
        const {
          x: left,
          y: top,
          w: width,
          h: height,
          rotate,
          moveSpeed,
          opacity,
        } = props.object;
        if (animation) {
          animation.pause(true);
        }
        animation = anime({
          targets: el.value,
          left,
          top,
          width,
          height,
          rotate,
          opacity,
          ...(moveSpeed > 1000 ? { easing: "linear" } : {}),
          duration: moveSpeed ?? config.animateDuration,
          update: () => {
            try {
              moveable.updateRect();
            } catch (error) {
              // pass
            }
          },
        });
      },
      { deep: true }
    );

    onMounted(() => {
      const { x, y, w, h, rotate } = props.object;
      el.value.style.width = `${w}px`;
      el.value.style.height = `${h}px`;
      el.value.style.left = `${x}px`;
      el.value.style.top = `${y}px`;
      el.value.style.transform = `rotate(${rotate}deg)`;
    });

    onUnmounted(() => {
      moveable.destroy();
    });

    const transformOrigin = computed(() => {
      const wearer = store.state.stage.board.objects.find(
        (a) => a.id === props.object.wornBy
      );
      if (wearer) {
        return `${wearer.x + wearer.w / 2 - props.object.x}px ${
          wearer.y + wearer.h / 2 - props.object.y
        }px`;
      } else {
        return "center";
      }
    });

    return { el, isDragging, clickInside, clickOutside, transformOrigin };
  },
};
</script>

<style>
</style>