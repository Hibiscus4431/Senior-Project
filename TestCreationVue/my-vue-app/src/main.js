import Vue from 'vue';
import {createApp} from 'vue';
import App from './App.vue';
import router from './router'; // Import the router

Vue.config.productionTip = false;
//create the application
const app = createApp(App);
// mount application?
app.mount('#app');
// new Vue({
//   render: h => h(App),
// }).$mount('#app');

new Vue({
  render: (h) => h(App),
  router, // Use the router
}).$mount('#app');
