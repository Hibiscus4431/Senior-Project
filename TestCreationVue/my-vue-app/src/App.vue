<template>
  <div id="app">
    <Welcome />
    <WebmasterLog />
    <WebmasterHome />
    <TeacherLog />
    <TeacherHome />
  </div>
</template>

<script>
import Welcome from './components/Welcome.vue';
import WebmasterLog from './components/WebmasterLog.vue';
import WebmasterHome from './components/WebmasterHome.vue';
import TeacherLog from './components/TeacherLog.vue';
import TeacherHome from './components/TeacherHome.vue';

export default {
  name: 'App',
  components: {
    Welcome,
    WebmasterLog,
    WebmasterHome,
    TeacherLog,
    TeacherHome
  }
}
</script>

<style>
/* Global styles can be added here */
</style>