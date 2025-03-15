import Vue from 'vue';
import Router from 'vue-router';
import Welcome from '../components/Welcome.vue';
import PubHome from '../components/PubHome.vue';
import PubLog from '../components/PubLog.vue';
import PubNewBook from '../components/PubNewBook.vue';
import PubNewTB from '../components/PubNewTB.vue';
import PubQuestions from '../components/PubQuestions.vue';
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

Vue.use(Router);

const routes = [
    {
        path: '/',
        name: 'Welcome',
        component: Welcome, // The homepage
      },
      {
        path: '/pub-home',
        name: 'PubHome',
        component: PubHome, // Public home page
      },
      {
        path: '/pub-log',
        name: 'PubLog',
        component: PubLog, // Public login page
      },
      {
        path: '/pub-new-book',
        name: 'PubNewBook',
        component: PubNewBook, // New book page
      },
      {
        path: '/pub-new-tb',
        name: 'PubNewTB',
        component: PubNewTB, // New TB page
      },
      {
        path: '/pub-questions',
        name: 'PubQuestions',
        component: PubQuestions, // Public questions page
      },
      {
        path: '/pub-view-tb',
        name: 'PubViewTB',
        component: PubViewTB, // View TB page
      },
      {
        path: '/teacher-home',
        name: 'TeacherHome',
        component: TeacherHome, // Teacher home page
      },
      {
        path: '/teacher-log',
        name: 'TeacherLog',
        component: TeacherLog, // Teacher login page
      },
      {
        path: '/teacher-new-class',
        name: 'TeacherNewClass',
        component: TeacherNewClass, // Teacher new class page
      },
      {
        path: '/teacher-new-tb',
        name: 'TeacherNewTB',
        component: TeacherNewTB, // Teacher new TB page
      },
      {
        path: '/teacher-new-test',
        name: 'TeacherNewTest',
        component: TeacherNewTest, // Teacher new test page
      },
      {
        path: '/teacher-pub-q',
        name: 'TeacherPubQ',
        component: TeacherPubQ, // Teacher publish questions page
      },
      {
        path: '/teacher-questions',
        name: 'TeacherQuestions',
        component: TeacherQuestions, // Teacher questions page
      },
      {
        path: '/teacher-template',
        name: 'TeacherTemplate',
        component: TeacherTemplate, // Teacher template page
      },
      {
        path: '/teacher-view-tb',
        name: 'TeacherViewTB',
        component: TeacherViewTB, // Teacher view TB page
      },
      {
        path: '/webmaster-home',
        name: 'WebmasterHome',
        component: WebmasterHome, // Webmaster home page
      },
      {
        path: '/webmaster-log',
        name: 'WebmasterLog',
        component: WebmasterLog, // Webmaster login page
      },
];

export default new Router({
    mode: 'history',
    routes
});