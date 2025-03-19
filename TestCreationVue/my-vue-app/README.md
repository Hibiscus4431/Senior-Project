# my-vue-app/my-vue-app/README.md

# My Vue App

## Project Overview

This project is a Vue.js application that serves as a Test Creation Manager. It allows users to log in as different roles, including Teacher, Publisher, and Webmaster.

## Project Structure

```
my-vue-app
├── src
│   ├── components
│   │   └── Welcome.vue      # Vue component for the welcome page
│   ├── App.vue              # Root component of the Vue application
│   └── main.js              # Entry point of the Vue application
├── package.json             # Configuration file for npm
├── README.md                # Documentation for the project
└── vue.config.js            # Configuration file for Vue CLI
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