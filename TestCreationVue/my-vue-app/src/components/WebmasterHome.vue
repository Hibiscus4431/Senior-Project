<template>
  <div class="webmaster-home-container">
    <div class="center large-heading">
      <h1>Database Downloads</h1>
    </div>

    <div class="center large-paragraph">
      <p>Select a dataset to download:</p>
      <button class="button" @click="downloadData('users')">Download Users</button>
      <button class="button" @click="downloadData('textbooks')">Download Textbooks</button>
      <button class="button" @click="downloadData('courses')">Download Courses</button>
      <button class="button" @click="downloadData('questions')">Download Questions</button>
      <button class="button" @click="downloadData('tests')">Download Tests</button>
      <button class="button" @click="downloadData('all')">Download All</button>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'WebmasterHome',
  methods: {
    async downloadData(type) {
      try {
        const response = await fetch(`${process.env.VUE_APP_API_URL}/download/users`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });


        if (!response.ok) {
          throw new Error(`Failed to download ${type}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `${type === 'all' ? 'all_data.txt' : `${type}.csv`}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Download error:', error);
        alert(`Failed to download ${type} data.`);
      }
    }
  }
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
  align-items: center;
  padding-top: 50px;
}

.button {
  margin: 10px;
  padding: 12px 24px;
  font-size: 16px;
  background-color: #00bcd4;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 6px;
}

.button:hover {
  background-color: #0192a0;
}
</style>