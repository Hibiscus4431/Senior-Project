# my-vue-app/README.md

# My Vue App

## Project Overview

This project is a Vue.js application that serves as a Test Creation Manager. It allows users to log in as different roles, including Teacher, Publisher, and Webmaster.

## Project Structure

```
my-vue-app
├── src
│   ├── assets
│   │   |── publisher_styles.css # Styling formats for the publisher pages
│   │   |── teacher_styles.css   # Styling formats for the teacher pages
│   │   |── webmaster_styles.css # Styling formats for the webmaster pages
│   ├── components
│   │   |── PubHome.vue          # Vue component for the Publisher Home page
│   │   |── PubLog.vue           # Vue component for the Publisher Login page
│   │   |── PubNewBook.vue       # Vue component for the Publisher Book Creation page
│   │   |── PubQuestions.vue     # Vue component for the Publisher Question page
│   │   |── PubViewTB.vue        # Vue component for the Publisher Testbank view page
│   │   |── TeacherHome.vue      # Vue component for the Teacher Home page
│   │   |── TeacherLog.vue       # Vue component for the Teacher Login page
│   │   |── TeacherNewClass.vue  # Vue component for the Teacher Class Creation page
│   │   |── TeacherNewTB.vue     # Vue component for the Teacher Testbank Creation page
│   │   |── TeacherNewTest.vue   # Vue component for the Teacher Test Options page
│   │   |── TeacherPubQ.vue      # Vue component for the Teacher view Pub Questions page
│   │   |── TeacherPubTB.vue     # Vue component for the Teacher view Pub Testbanks page
│   │   |── TeacherQuestions.vue # Vue component for the Teacher Question page
│   │   |── TeacherTemplate.vue  # Vue component for the Teacher viewing the Test page
│   │   |── TeacherViewTB.vue    # Vue component for the Teacher Testbank View page
│   │   |── WebmasterHome.vue    # Vue component for the Webmaster Home page
│   │   |── WebmasterLog.vue     # Vue component for the Webmaster Login page
│   │   └── Welcome.vue          # Vue component for the welcome page
│   ├── router
│   │   |── index.js             # Routing table for the Vue application
│   ├── App.vue                  # Root component of the Vue application
│   └── main.js                  # Entry point of the Vue application
├── package.json                 # Configuration file for npm
├── README.md                    # Documentation for the project
└── vue.config.js                # Configuration file for Vue CLI
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd my-vue-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the application:**
   ```bash
   npm run serve
   ```

4. **Open your browser:**
   Navigate to `http://localhost:8080` to view the application.

## Usage Guidelines

- Upon accessing the application, users will be presented with a welcome page where they can select their role to log in.
- Each role will redirect to a specific login page.

## License

This project is licensed under the MIT License.