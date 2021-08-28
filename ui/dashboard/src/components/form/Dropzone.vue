<script setup>
import { defineEmits, ref } from "@vue/runtime-core";
import { imageExtensions } from '@/utils/constants'

const emit = defineEmits(['change']);

const el = ref();

const onChange = () => {
  emit('change', el.value.files)
  el.value.value = ''
};
const dragover = (event) => {
  event.preventDefault();
  // Add some visual fluff to show the user can drop its files
  if (!event.currentTarget.classList.contains('active')) {
    event.currentTarget.classList.remove('inactive');
    event.currentTarget.classList.add('active');
  }
};
const dragleave = (event) => {
  // Clean up
  event.currentTarget.classList.add('inactive');
  event.currentTarget.classList.remove('active');
};
const drop = (event) => {
  event.preventDefault();
  el.value.files = event.dataTransfer.files;
  // Clean up
  event.currentTarget.classList.add('inactive');
  event.currentTarget.classList.remove('active');
}

</script>
      
  <template>
  <div @dragover="dragover" @dragleave="dragleave" @drop="drop">
    <input
      ref="el"
      type="file"
      multiple
      id="dropzone"
      @change="onChange"
      :accept="imageExtensions"
      style="display: none;"
    />
    <label for="dropzone">
      <slot>
        <div class="button is-dark upload-frame">
          <i class="fas fa-upload"></i>
          <span>Drag files here or click to upload</span>
        </div>
      </slot>
    </label>
  </div>
</template>
      
<style lang="scss" scoped>
.upload-frame {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100px;
}
.active {
  transform: scale(1.2);
  transition-duration: 0.5s;
}
</style>
    
  