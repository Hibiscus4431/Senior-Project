<template>
  <div id="app">
    <Welcome />
    <WebmasterLog />
    <WebmasterHome />
    <TeacherLog />
    <TeacherHome />
    <TeacherNewClass />
    <TeacherQuestions />
    <TeacherViewTB />
    <TeacherNewTB />
    <TeacherNewTest />
    <TeacherPubQ />
    <TeacherPubTB />
    <TeacherTemplate />
  </div>
</template>

<script>
import Welcome from './components/Welcome.vue';
import WebmasterLog from './components/WebmasterLog.vue';
import WebmasterHome from './components/WebmasterHome.vue';
import TeacherLog from './components/TeacherLog.vue';
import TeacherHome from './components/TeacherHome.vue';
import TeacherNewClass from './components/TeacherNewClass.vue';
import TeacherQuestions from './components/TeacherQuestions.vue';
import TeacherViewTB from './components/TeacherViewTB.vue';
import TeacherNewTB from './components/TeacherNewTB.vue';
import TeacherNewTest from './components/TeacherNewTest.vue';
import TeacherPubQ from './components/TeacherPubQ.vue';
import TeacherPubTB from './components/TeacherPubTB.vue';
import TeacherTemplate from './components/TeacherTemplate.vue';

export default {
  name: 'App',
  components: {
    Welcome,
    WebmasterLog,
    WebmasterHome,
    TeacherLog,
    TeacherHome,
    TeacherNewClass,
    TeacherQuestions,
    TeacherViewTB,
    TeacherNewTB,
    TeacherNewTest,
    TeacherPubQ,
    TeacherPubTB,
    TeacherTemplate
  }
}
</script>

<style>
/* Global styles can be added here */
</style>