<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/WebmasterHome.vue -->
<template>
    <div class="webmaster-home-container">
        <div class="center large-heading">
            <h1> Welcome Webmaster</h1>
        </div>

        <div class="center large-paragraph">
            View website as:
            <br><br>
            <!-- TODO:replace w/ teacher vue homepage-->
            <router-link to="/TeacherHome">
                <button class="button">Teacher</button>
            </router-link>
            <br>
            <br>
            <!-- TODO: replace w/ publisher vue homepage-->
            <router-link to="/PubHome">
                <button class="button">Publisher</button>
            </router-link>
        </div>
    </div>
</template>

<script>
export default {
    name: 'WebmasterHome'
};
</script>

<style scoped>
@import '../assets/webmaster_styles.css';

.webmaster-home-container {
    background-color: #082e75;
    font-family: Arial, sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
}
</style>