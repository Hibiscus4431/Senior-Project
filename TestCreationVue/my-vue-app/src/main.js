import Vue from 'vue';
import {createApp} from 'vue';
import App from './App.vue';

Vue.config.productionTip = false;
//create the application
const app = createApp(App);
// mount application?
app.mount('#app');
// new Vue({
//   render: h => h(App),
// }).$mount('#app');

