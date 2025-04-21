<template>
  <div class="theme-webmaster">
    <div class="top-banner">
      <div class="banner-title">Database Downloads</div>

      <div class="banner-actions">
        <router-link to="/" class="banner-btn">Log Out</router-link>
      </div>
    </div>

    <div class="center large-paragraph" style="color: #222;">
      <div class="page-wrapper" style="font-size: 24px; text-align: center;">
        <h1>Select a dataset to download:</h1>
        <br>
       <strong>Note:</strong> Download All will download each file separately for readability.
       <hr>
        <div class="button-row">
          <button class="button" @click="downloadData('users')">Download Users</button>
          <button class="button" @click="downloadData('textbook')">Download Textbooks</button>
          <button class="button" @click="downloadData('courses')">Download Courses</button>
          <button class="button" @click="downloadData('questions')">Download Questions</button>
          <!-- <button class="button" @click="downloadData('tests')">Download Tests</button> -->
          <button class="button" @click="downloadData('all')">Download All</button>
        </div>
      </div>
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
      }
    }
  }
};
</script>


<style scoped>
@import '../assets/webmaster_styles.css';
</style>