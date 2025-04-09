// /src/router/index.js (or similar)
import { createRouter, createWebHistory } from 'vue-router';
import Welcome from '../components/Welcome.vue';
import PubHome from '../components/PubHome.vue';
import PubLog from '../components/PubLog.vue';
import PubNewBook from '../components/PubNewBook.vue';
import PubNewTB from '../components/PubNewTB.vue';
import PubQuestions from '../components/PubQuestions.vue';
import PubViewFeedback from '../components/PubViewFeedback.vue';
import PubViewTB from '../components/PubViewTB.vue';
import TeacherHome from '../components/TeacherHome.vue';
import TeacherLog from '../components/TeacherLog.vue';
import TeacherNewClass from '../components/TeacherNewClass.vue';
import TeacherNewTB from '../components/TeacherNewTB.vue';
import TeacherNewTest from '../components/TeacherNewTest.vue';
import TeacherPubQ from '../components/TeacherPubQ.vue';
import TeacherQuestions from '../components/TeacherQuestions.vue';
import TeacherTemplate from '../components/TeacherTemplate.vue';
import TeacherViewTB from '../components/TeacherViewTB.vue';
import WebmasterHome from '../components/WebmasterHome.vue';
import WebmasterLog from '../components/WebmasterLog.vue';

const routes = [
  { path: '/', name: 'Welcome', component: Welcome },
  { path: '/PubHome', name: 'PubHome', component: PubHome },
  { path: '/PubLog', name: 'PubLog', component: PubLog },
  { path: '/PubNewBook', name: 'PubNewBook', component: PubNewBook },
  { path: '/PubNewTB', name: 'PubNewTB', component: PubNewTB },
  { path: '/PubQuestions', name: 'PubQuestions', component: PubQuestions },
  { path: '/PubViewFeedback', name: 'PubViewFeedback', component: PubViewFeedback },
  { path: '/PubViewTB', name: 'PubViewTB', component: PubViewTB },
  { path: '/TeacherHome', name: 'TeacherHome', component: TeacherHome },
  { path: '/TeacherLog', name: 'TeacherLog', component: TeacherLog },
  { path: '/TeacherNewClass', name: 'TeacherNewClass', component: TeacherNewClass },
  { path: '/TeacherNewTB', name: 'TeacherNewTB', component: TeacherNewTB },
  { path: '/TeacherNewTest', name: 'TeacherNewTest', component: TeacherNewTest },
  { path: '/TeacherPubQ', name: 'TeacherPubQ', component: TeacherPubQ },
  { path: '/TeacherQuestions', name: 'TeacherQuestions', component: TeacherQuestions },
  { path: '/TeacherTemplate', name: 'TeacherTemplate', component: TeacherTemplate },
  { path: '/TeacherViewTB/:id', name: 'TeacherViewTB', component: TeacherViewTB },
  { path: '/WebmasterHome', name: 'WebmasterHome', component: WebmasterHome },
  { path: '/WebmasterLog', name: 'WebmasterLog', component: WebmasterLog },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
