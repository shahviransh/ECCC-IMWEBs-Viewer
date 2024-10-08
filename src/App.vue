<template>
  <div id="app">
    <!-- Top Bar -->
    <header class="top-bar">
      <h2>IMWEBs Viewer</h2>
    </header>

    <!-- Taskbar -->
    <nav class="taskbar">
      <div class="taskbar-left">
        <button @click="selectFolder">📁 Select Folder</button>
        <span class="folder-path">{{ folderPath }}</span>
        <!-- Placeholder for additional tools components -->
      </div>
      <div class="taskbar-right">
        <button v-for="page in pages" :key="page" :class="{ active: page === activePage }"  @click="navigateTo(page)">{{ page }}</button>
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
  /* Prevent the whole page from scrolling */
}

body,
html {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
  /* Ensure no scroll at the global level */
}

.top-bar {
  background-color: #b85b14;
  padding:  1px;
  color: #fff;
}

.taskbar {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #35495e;
  color: #fff;
}

.taskbar button {
  background-color: transparent;
  color: #fff;
  border: none;
  margin: 0 5px;
  cursor: pointer;
}

.taskbar button.active {
  background-color: #009879; /* Highlight color */
  color: white;
}
</style>