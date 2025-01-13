<template>
  <div class="message-container">
    <transition-group name="fade" tag="div">
      <div v-for="(msg, index) in messages" :key="index" :class="['message-box', msg.type]">
        <div class="message-content">
          <span>{{ msg.text }}</span>
          <button @click="removeMessage(index)" class="close-button">✕</button>
        </div>
        <div class="countdown-bar" :style="{ width: (msg.timeLeft / msg.totalTime * 100) + '%' }"></div>
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
    startTimer(msg) {
      const interval = setInterval(() => {
        if (msg.timeLeft > 0) {
          msg.timeLeft -= 1;
        } else {
          this.removeMessage(this.messages.indexOf(msg));
          clearInterval(interval);
        }
      }, 0);
    },
    removeMessage(index) {
      this.sliceMessage(index);
    }
  },
  watch: {
    messages: {
      handler(newVal) {
        if (newVal.length > 0) {
          this.messages.forEach(msg => {
            if (!msg.intervalId) { // Only start timer if not already started
              this.startTimer(msg);
            }
          });
        }
      },
      deep: true
    }
  }
};
</script>

<style scoped>
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

.message-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  max-width: 300px;
  z-index: 9999;
}

.message-box {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: start;
  justify-content: space-between;
  padding: 10px 15px;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  margin-bottom: 10px;
  transition: opacity 0.3s ease;
}

.message-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.countdown-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.5);
  width: 100%;
}

.close-button {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2em;
  cursor: pointer;
  margin-left: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>