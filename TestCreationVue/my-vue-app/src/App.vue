
<template>
  <div id="app">
    <!-- This is where the route's component will be displayed -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
  name: 'App',
  mounted() {
    document.title = "Print-A-Test"; // Change this to your desired app name
  }
};
</script>
<style>
html, body {
  margin: 0; /* Remove default margin */
  padding: 0; /* Remove default padding */
  
}


</style>