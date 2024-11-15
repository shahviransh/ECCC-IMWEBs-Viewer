<template>
    <div class="message-container">
      <transition-group name="fade" tag="div">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-box', msg.type]"
        >
          <span>{{ msg.text }}</span>
          <button @click="sliceMessage(index)" class="close-button">✕</button>
        </div>
      </transition-group>
    </div>
  </template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    name: 'MessageBox',
    computed: {
        ...mapState(["messages"]),
    },
    methods: {
        ...mapActions(["pushMessage", "sliceMessage"]),
    },
};
</script>

<style scoped>
.message-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  max-width: 300px;
  z-index: 9999;
}

.message-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 15px;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  margin-bottom: 10px;
  transition: opacity 0.3s ease;
}

.message-box.info {
  background-color: #2196f3;
}

.message-box.success {
  background-color: #4caf50;
}

.message-box.warning {
  background-color: #ff9800;
}

.message-box.error {
  background-color: #f44336;
}

.close-button {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2em;
  cursor: pointer;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>