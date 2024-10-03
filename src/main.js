import { createApp } from 'vue';
import App from './App.vue';
import store from './store'; // Import the Vuex store

createApp(App)
  .use(store) // Register Vuex store
  .mount('#app');