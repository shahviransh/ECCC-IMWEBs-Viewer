<template>
  <div id="papp" :class="theme">
    <!-- Top Bar -->
    <header class="top-bar">
      <div class="title-container">
        <h2>IMWEBs Viewer</h2>
      </div>
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
import { open } from "@tauri-apps/plugin-dialog";
import { dirname } from "@tauri-apps/api/path";

export default {
  name: "App",
  data() {
    return {
      pages: [
        "Project",
        "Table",
        "Graph",
        "Map",
        "Calibration",
        "BMP",
        "Tools",
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
  },
  mounted() {
    // Set initial theme on load
    document.body.className = this.theme;
    this.updatePageTitle(this.activePage);
    this.$router.push({ name: this.activePage });
  },
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
  min-height: 100vh;
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
</style>