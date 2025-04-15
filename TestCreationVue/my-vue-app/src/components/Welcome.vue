<!-- filepath: /c:/Users/laure/Senior-Project/TestCreationVue/src/components/Welcome.vue -->
<template>

        <div class="theme-welcome">
            <div class="top-banner">
                <div class="banner-title">Welcome to Print-A-Test</div>
            </div>
            <div class="center large-paragraph" style="color:#222"> 
                Select the role you are logging in as:</div>
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
</template>

<script>
export default {
    name: 'Welcome'
}
</script>

<style scoped>
.button {
    background-color: var(--banner-color);
    border: none;
    color: #222;
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
.button:hover {
  background-color: #cf685f;
}

.center {
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

.theme-welcome {
    --banner-color: #d2746b;
    --text-color: #222;
    --card-bg: #ffffff;
    /* ✅ Define this missing variable */
    background-color: #fdfdfd;
    min-height: 100vh;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.top-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    /* ✅ allows wrap on small screens */
    gap: 20px;
    padding: 15px 30px;
    background-color: var(--banner-color);
    color: var(--text-color);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 999;
}

/* Larger submit button */
input[type="submit"] {
    background-color: #f1af15;
    color: black;
    font-size: 20px;
    padding: 10px 20px;
}
</style>