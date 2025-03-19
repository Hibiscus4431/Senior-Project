<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/Welcome.vue -->
<template>
    <div class="Welcome-container">
        <div>
            <h1 class="center large-heading"> Welcome to Test Creation Manager</h1>
            <div class="center large-paragraph"> Select the role you are logging in as:</div>
            <br>
            <br>
            <div class="button-container">
                <router-link to="/TeacherLog">
                    <button class="button">Teacher</button>
                </router-link>
            </div>
            <br>
            <div class="button-container">
                <router-link to="/PubLog">
                    <button class="button">Publisher</button>
                </router-link>
            </div>
            <br>
            <div class="button-container">
                <router-link to="/WebmasterLog">
                    <button class="button">Webmaster</button>
                </router-link>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Welcome'
}
</script>

<style scoped>
.button {
    background-color: rgb(150, 29, 18);
    border: none;
    color: white;
    padding: 10px 15px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 25px;
    margin: 4px 2px;
    cursor: pointer;
}

.button-container {
    text-align: center;
    display: flex;
    justify-content: center;
    margin: 10px 0;
}

.center {
    color: white;
    text-align: center;
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 50%;
}

.large-heading {
    font-size: 55px;
}

.large-paragraph {
    font-size: 30px;
}

.Welcome-container {
    background-color: #2a2b2b !important;
    font-family: Arial, sans-serif;
    height: 100vh;
    height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>