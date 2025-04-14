<template>
  <div class="webmaster-home-container">
    <div class="center large-heading">
      <h1>Database Downloads</h1>
    </div>

    <div class="center large-paragraph">
      <p>Select a dataset to download:</p>
      <p>Note: Download All will download each file separately for readability.</p>
      <button class="button" @click="downloadData('users')">Download Users</button>
      <button class="button" @click="downloadData('textbook')">Download Textbooks</button>
      <button class="button" @click="downloadData('courses')">Download Courses</button>
      <button class="button" @click="downloadData('questions')">Download Questions</button>
      <!-- <button class="button" @click="downloadData('tests')">Download Tests</button> -->
      <button class="button" @click="downloadData('all')">Download All</button>
    </div>
  </div>
</template>

<script>
import api from '@/api'; // using your configured axios instance

export default {
  name: 'WebmasterHome',
  methods: {
    async downloadData(type) {
      const endpoints = {
        users: 'users',
        courses: 'courses',
        textbook: 'textbook',
        questions: 'questions'
      };

      if (type === 'all') {
        for (const [key, endpoint] of Object.entries(endpoints)) {
          await this.fetchAndDownload(endpoint, `${key}.csv`);
        }
        return;
      }

      const endpoint = endpoints[type];
      if (!endpoint) {
        alert(`Unsupported download type: ${type}`);
        return;
      }

      await this.fetchAndDownload(endpoint, `${type}.csv`);
    },

    async fetchAndDownload(endpoint, filename) {
      try {
        const response = await api.get(`/download/${endpoint}`, {
          responseType: 'blob'
        });

        const url = window.URL.createObjectURL(response.data);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error(`Download error for ${endpoint}:`, error);
        alert(`Failed to download ${filename}`);
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