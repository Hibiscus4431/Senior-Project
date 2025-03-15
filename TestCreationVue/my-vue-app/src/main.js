import Vue from 'vue';
import App from './App.vue';
import router from './router'; // Import the router

Vue.config.productionTip = false;

new Vue({
  render: (h) => h(App),
  router, // Use the router
}).$mount('#app');