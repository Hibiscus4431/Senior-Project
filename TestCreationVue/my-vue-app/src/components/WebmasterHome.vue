<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/WebmasterHome.vue -->
 <template>
      <div class="center large-heading">
        <h1> Welcome Webmaster</h1>
    </div>

    <div class="center large-paragraph">
        View website as:
        <br><br>
        <!-- TODO:replace w/ teacher vue homepage-->
         <router-link to="/Teacher_hp">
            <button class="button">Teacher</button>
        </router-link>
        <br>
        <br>
        <!-- TODO: replace w/ publisher vue homepage-->
        <router-link to="/Pub_hp">
            <button class="button">Publisher</button>
        </router-link>
    </div>
 </template>

 <script>
    export default {
        name: 'WebmasterHome'
    };
</script>

<style scoped>
    @import '../assets/webmaster_styles.css';
</style>