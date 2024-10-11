<template>
  <div id="app" :class="theme">
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
        <span class="folder-path">{{ folderPath }}</span>
        <!-- Placeholder for additional tools components -->
      </div>
      <div class="taskbar-right">
        <button v-for="page in pages" :key="page" :class="{ active: page === activePage }" @click="navigateTo(page)">{{
          page }}</button>
      </div>
    </nav>

    <!-- Main Content -->
    <router-view></router-view>
  </div>
</template>

<script>

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
      folderPath: "",
      activePage: "Project", // Set default page here
      theme: "light", // Default theme
    };
  },
  methods: {
    selectFolder() {
      // Placeholder for selecting a folder, could be integrated with backend logic
      this.folderPath = "Jenette_Creek_Watershed";
    },
    navigateTo(page) {
      this.activePage = page; // Update active page
      this.$router.push({ name: page });
    },
    toggleTheme() {
      this.theme = this.theme === "light" ? "dark" : "light";
      document.body.className = this.theme; // Update body class for global styling
      this.$emit("themeChanged", this.theme); // Emit event to notify child components
    },
  },
  mounted() {
    // Set initial theme on load
    document.body.className = this.theme;
    this.$emit("themeChanged", this.theme); // Emit event to notify child components
  },
};
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  color: #2c3e50;
  margin: -8px;
  padding: 0px;
  text-align: center;
  overflow: hidden;
}

/* Apply theme variables */
.top-bar {
  background-color: var(--top-bar-bg);
  color: var(--top-bar-text);
  padding: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
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