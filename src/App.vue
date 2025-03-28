<template>
  <Loading v-if="isLoading" />
  <Login v-else-if="!isAuthenticated" v-model:isAuthenticated="isAuthenticated" />
  <div v-else id="papp" :class="theme">
    <!-- Top Bar -->
    <header class="top-bar">
      <div class="title-container">
        <h2>IMWEBs Viewer</h2>
      </div>
      <button class="logout-button" @click="logout">🚪 Logout</button>
      <button class="theme-switch" @click="toggleTheme">
        <span v-if="theme === 'light'">🌞</span>
        <span v-else>🌜</span>
      </button>
    </header>

    <!-- Taskbar -->
    <nav class="taskbar">
      <div class="taskbar-left">
        <button @click="selectFolder">📁 Select Folder</button>
        <span class="folder-path">{{ modelFolder }}</span>
        <!-- Placeholder for additional tools components -->
        <span v-if="activePage === 'Graph'">
          <button @click="handleZoomIn">Zoom In</button>
          <button @click="handleZoomOut">Zoom Out</button>
          <button @click="handleResetZoom">Reset Zoom</button>
        </span>
      </div>
      <div class="taskbar-right">
        <button v-for="page in pages" :key="page" :class="{ active: page === activePage }" @click="navigateTo(page)">{{
          page }}</button>
      </div>
    </nav>

    <!-- Main Content -->
    <router-view class="main-content" />
    <MessageBox />
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import MessageBox from "./components/MessageBox.vue";
import Login from "./pages/Login.vue";
import Loading from "./pages/Loading.vue";
import axios from "axios";
import { open } from "@tauri-apps/plugin-dialog";
import { dirname } from "@tauri-apps/api/path";

export default {
  name: "App",
  data() {
    return {
      isAuthenticated: false,
      isLoading: true,
      pages: [
        "Project",
        "Table",
        "Graph",
        "Map",
        "Help",
      ],
      activePage: "Project", // Set default page here
    };
  },
  computed: {
    ...mapState(["theme", "currentZoomStart", "modelFolder", "currentZoomEnd"]),
  },
  components: {
    MessageBox,
    Login,
    Loading,
  },
  methods: {
    ...mapActions(["updateTheme", "updatePageTitle", "updateCurrentZoom", "updateModelFolder"]),
    async selectFolder() {
      try {
        const selectedPath = await open({
          directory: false, // Allow both files and folders
          multiple: false, // Only allow one selection
        });

        if (selectedPath) {
          const folderPath = selectedPath.endsWith("/") ? selectedPath : await dirname(selectedPath);

          // Convert folder path to universal style
          const universalPath = folderPath.replace(/\\/g, "/");

          this.updateModelFolder(universalPath);
        }
      } catch (error) {
        console.error("Error selecting folder: ", error);
      }
    },
    navigateTo(page) {
      this.activePage = page; // Update active page
      this.updatePageTitle(this.activePage);
      this.$router.push({ name: page });
    },
    toggleTheme() {
      const theme = this.theme === "light" ? "dark" : "light";
      document.body.className = theme; // Update body class for global styling
      this.updateTheme(theme);
    },
    handleZoomIn() {
      if (this.currentZoomEnd - this.currentZoomStart > 10) {
        this.updateCurrentZoom({ start: this.currentZoomStart + 10, end: this.currentZoomEnd - 10 });
      }
    },
    handleZoomOut() {
      if (this.currentZoomStart > 0) {
        this.updateCurrentZoom({ start: this.currentZoomStart - 10, end: this.currentZoomEnd + 10 });
      }
    },
    handleResetZoom() {
      this.updateCurrentZoom({ start: 0, end: 100 });
    },
    async checkServerStatus() {
      // Check if the server is running, keep checking every 2 seconds
      const interval = setInterval(async () => {
        try {
          await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/health`);
          this.isLoading = false;
          clearInterval(interval); // Stop checking once successful
        } catch (error) {
          console.error("Server is not running", error);
        }
      }, 2000);
    },
    async checkAuth() {
      const token = localStorage.getItem("token");

      // Check if token is present and valid
      if (!token) {
        this.isAuthenticated = false;
        return;
      }
      try {
        // Verify token with the server
        const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/verify-token`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.isAuthenticated = response.status === 200;
      } catch {
        localStorage.removeItem("token");
        this.isAuthenticated = false;
      }
    },
    async logout() {
      try {
        // Clear token from local storage and logout from the server
        const token = localStorage.getItem("token");
        if (token) {
          await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/logout`, {}, {
            headers: { Authorization: `Bearer ${token}` },
          });
        }
      } catch (error) {
        console.error("Logout failed", error);
      } finally {
        localStorage.removeItem("token");
        this.isAuthenticated = false;
      }
    },
  },
  async mounted() {
    // Set initial theme on load
    document.body.className = this.theme;
    await this.checkServerStatus();
    await this.checkAuth();
  },
  watch: {
    isAuthenticated() {
      if (this.isAuthenticated) {
        this.updatePageTitle(this.activePage);
        this.$router.push({ name: this.activePage }); // Redirect after successful login
      }
    },
  }
};
</script>
<style>
html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>

<style scoped>
#papp {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  color: #2c3e50;
  text-align: center;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.top-bar {
  background-color: var(--top-bar-bg);
  color: var(--top-bar-text);
  padding: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.main-content {
  flex-grow: 1;
  height: 100%;
}

.title-container {
  flex-grow: 1;
  text-align: center;
}

.taskbar {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: var(--taskbar-bg);
  color: var(--taskbar-text);
}

.taskbar button {
  background-color: transparent;
  color: var(--taskbar-text);
  border: none;
  margin: 0 5px;
  cursor: pointer;
}

.taskbar-left {
  display: flex;
  align-items: center;
}

.taskbar button.active {
  background-color: var(--active-bg);
  color: white;
  border-radius: 5px;
}

/* Theme variables */
.light {
  --top-bar-bg: #b85b14;
  --top-bar-text: #fff;
  --taskbar-bg: #35495e;
  --taskbar-text: #fff;
  --active-bg: #009879;
}

.dark {
  --top-bar-bg: #1e1e1e;
  --top-bar-text: #e0e0e0;
  --taskbar-bg: #2d2d2d;
  --taskbar-text: #cfcfcf;
  --active-bg: #5a5a5a;
}

.theme-switch {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--top-bar-text);
}

.logout-button {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--top-bar-text);
  margin-left: 10px;
}
</style>