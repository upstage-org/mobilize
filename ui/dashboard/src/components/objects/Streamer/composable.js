import { onMounted, ref, watch } from "vue";
import { cropImageFromCanvas } from "@/utils/canvas";
import flvjs from "flv.js";

export const useShape = (video, object) => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const src = ref();

    const draw = () => {
        if (video.value) {
            ctx.drawImage(video.value, 0, 0, object.w, object.h);
            src.value = cropImageFromCanvas(canvas)?.src;
        }
    }

    const loop = () => {
        if (!video.value.paused && !video.value.ended) {
            draw();
            requestAnimationFrame(loop);
        }
    }

    onMounted(() => video.value.addEventListener('play', loop))

    const clipImage = (src) => new Promise(resolve => {
        const img = document.createElement('img');
        img.onload = function () {
            ctx.drawImage(img, 0, 0, object.w, object.h);
            ctx.globalCompositeOperation = 'source-in';
            resolve();
        };
        img.onerror = () => {
            resolve();
        }
        img.src = src;
    })

    watch(() => object.shape, async () => {
        const { shape } = object;
        const r = Math.min(object.w, object.h) / 2;
        canvas.width = object.w;
        canvas.height = object.h;
        switch (shape) {
            case 'circle':
                ctx.beginPath();
                ctx.arc(r, r, r, 0, Math.PI * 2, true);
                ctx.clip();
                break;

            case null:
                ctx.restore();
                break;

            default:
                await clipImage(shape);
        }
        draw();
    }, { immediate: true })

    return { src }
}

export const useFlv = (video, src) => {
    const playable = ref(flvjs.isSupported());

    const initPlayer = () => {
        if (flvjs.isSupported()) {
            const flvPlayer = flvjs.createPlayer({
                type: "flv",
                url: src.value,
            });
            flvPlayer.on('error', (e) => {
                console.log('error', e)
                playable.value = false
            })
            flvPlayer.attachMediaElement(video.value);
            flvPlayer.load();
        }
    };

    onMounted(initPlayer);
    watch(src, initPlayer);

    return { playable }
}