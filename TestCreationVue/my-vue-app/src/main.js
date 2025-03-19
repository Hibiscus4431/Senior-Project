import { createApp } from 'vue';
import App from './App.vue';
import router from './router';  // Assuming your router is in the `router/index.js` file

const app = createApp(App);
app.use(router);
app.mount('#app');