<template>
  <div id="app">
    <!-- Top Bar -->
    <header class="top-bar">
      <h1>IMWEBs Viewer</h1>
    </header>

    <!-- Taskbar -->
    <nav class="taskbar">
      <div class="taskbar-left">
        <button @click="selectFolder">📁 Select Folder</button>
        <span class="folder-path">{{ folderPath }}</span>
        <!-- Placeholder for additional tools components -->
      </div>
      <div class="taskbar-right">
        <button v-for="page in pages" :key="page" @click="navigateTo(page)">{{ page }}</button>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="content">
      <div class="left-panel">
        <!-- Component 1: Folder Navigation -->
        <div class="folder-navigation">
          <DatabaseDropdown />
          <TableDropdown :selectedDb="selectedDb" />
        </div>
        <!-- Component 2: Column Navigation -->
        <div class="column-navigation">
          <ColumnDropdown :selectedTable="selectedTable" />
        </div>
      </div>

      <!-- Component 3: Selection, Interval, Aggregation, and Export Config -->
      <div class="settings-panel">
        <Selection />
        <IntervalDropdown />
        <StatisticsDropdown />
        <AggregationMethod />
        <ExportConfig />
        <button class="fetch-button" @click="fetchData">Fetch Data</button>
        <button class="export-button" @click="exportData">Export Data</button>
        <h4 v-if="exportFilename">Saved {{ exportFilename }} to {{ exportPath }} as a {{ exportFormat }}</h4>
      </div>

      <!-- Component 4: Main View (Table and Stats Display) -->
      <div class="main-view">
        <!-- Table Container with Scrollable Body -->
        <div class="table-container">
          <table class="styled-table">
            <thead>
              <tr>
                <th v-for="column in selectedColumns" :key="column">{{ column }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in visibleData" :key="index">
                <td v-for="column in selectedColumns" :key="column">{{ row[column] }}</td>
              </tr>
            </tbody>
          </table>
          <!-- Load More Button -->
          <div v-if="canLoadMore" class="load-more-container">
            <button class="load-more-button" @click="loadMoreRows">Load More</button>
          </div>
        </div>
        <!-- Stats Container with Scrollable Body -->
        <div class="stats-container">
          <table class="styled-table">
            <thead>
              <tr>
                <th v-for="column in statsColumns" :key="column">{{ column }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in stats" :key="index">
                <td v-for="column in statsColumns" :key="column">{{ row[column] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import DatabaseDropdown from "./components/DatabaseDropdown.vue";
import TableDropdown from "./components/TableDropdown.vue";
import ColumnDropdown from "./components/ColumnDropdown.vue";
import Selection from "./components/Selection.vue";
import IntervalDropdown from "./components/IntervalDropdown.vue";
import AggregationMethod from "./components/AggregationMethod.vue";
import StatisticsDropdown from "./components/StatisticsDropdown.vue";
import ExportConfig from "./components/ExportConfig.vue";
import axios from 'axios';

export default {
  name: "App",
  components: {
    DatabaseDropdown,
    TableDropdown,
    ColumnDropdown,
    Selection,
    IntervalDropdown,
    AggregationMethod,
    StatisticsDropdown,
    ExportConfig,
  },
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
      stats: [],
      statsColumns: [],
      visibleData: [],
      rowLimit: 100,
      canLoadMore: true,
      data: [],
    };
  },
  computed: {
    ...mapState(["selectedDb", "selectedTable", "selectedColumns", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions"]),
  },
  methods: {
    selectFolder() {
      // Placeholder for selecting a folder, could be integrated with backend logic
      this.folderPath = "Jenette_Creek_Watershed";
    },
    loadInitialRows() {
      this.visibleData = this.data.slice(0, this.rowLimit);
      this.canLoadMore = this.data.length > this.rowLimit;
    },
    loadMoreRows() {
      const nextRowLimit = this.visibleData.length + this.rowLimit;
      const nextRows = this.data.slice(this.visibleData.length, nextRowLimit);
      // Append the next rows to the visible data
      this.visibleData = [...this.visibleData, ...nextRows];
      // Check if we can load more rows
      if (this.visibleData.length >= this.data.length) {
        this.canLoadMore = false; // Hide the load more button
      }
    },
    async fetchData() {
      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/get_data`, {
          params: {
            db_path: this.selectedDb,
            table_name: this.selectedTable,
            columns: this.selectedColumns.join(","),
            id: this.selectedIds.join(","),
            start_date: this.dateRange.start,
            end_date: this.dateRange.end,
            date_type: this.dateType,
            interval: this.selectedInterval,
            statistics: this.selectedStatistics.join(","),
            method: this.selectedMethod.join(","),
          }
        });
        this.data = response.data.data;
        this.stats = response.data.stats;
        this.statsColumns = response.data.statsColumns;
        this.loadInitialRows();
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
    async exportData() {
      try {
        await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/export_data`, {
          params: {
            db_path: this.selectedDb,
            table_name: this.selectedTable,
            columns: this.exportColumns.join(","),
            id: this.exportIds.join(","),
            start_date: this.exportDate.start,
            end_date: this.exportDate.end,
            date_type: this.exportDateType,
            interval: this.exportInterval,
            statistics: this.selectedStatistics.join(","),
            method: this.exportMethod,
            export_path: this.exportPath,
            export_filename: this.exportFilename,
            export_format: this.exportFormat,
            options: this.exportOptions,
          }
        });
      } catch (error) {
        console.error('Error exporting data:', error);
      }
    },
    navigateTo(page) {
      switch (page) {
        case "Project":
          this.$router.push({ name: "Project" });
          break;
        case "Table":
          this.$router.push({ name: "Table" });
          break;
        case "Graph":
          this.$router.push({ name: "Graph" });
          break;
        case "Map":
          this.$router.push({ name: "Map" });
          break;
        case "Calibration":
          this.$router.push({ name: "Calibration" });
          break;
        case "BMP":
          this.$router.push({ name: "BMP" });
          break;
        case "Tools":
          this.$router.push({ name: "Tools" });
          break;
        case "Help":
          this.$router.push({ name: "Help" });
          break;
        default:
          console.error(`Unknown page: ${page}`);
      }
    },
  },
};
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  color: #2c3e50;
  margin: 0;
  padding: 0;
  text-align: center;
  overflow: hidden; /* Prevent the whole page from scrolling */
}

body, html {
  margin: 0;
  padding: 0;
  height: 85%;
  overflow: hidden; /* Ensure no scroll at the global level */
}

.top-bar {
  background-color: #42b983;
  padding: 1px;
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

.content {
  display: flex;
  flex-direction: row;
  height: calc(100vh - 100px); /* Adjust to the viewport, minus top bar and taskbar */
}

.left-panel {
  display: flex;
  flex-direction: column;
  width: 25%; /* Takes 1/4 of the horizontal space */
  height: 85%; /* Ensure full height */
  overflow: hidden;
}

.folder-navigation {
  margin: 0;
  border: 1px solid #ddd;
  padding: 10px;
  height: 35%; /* Takes 1/4 of the vertical space */
  overflow-y: auto;
}

.column-navigation {
  margin: 0;
  border: 1px solid #ddd;
  padding: 0px;
  height: 80%; /* Takes the remaining vertical space */
  overflow-y: auto;
}

.settings-panel {
  width: 50%; /* Takes 2/4 of the horizontal space */
  height: 85%; /* Ensure full height */
  margin: 10px;
  border: 1px solid #ddd;
  padding: 10px;
  overflow-y: auto;
}

.main-view {
  width: 50%; /* Takes 2/4 of the horizontal space */
  height: 85%; /* Ensure full height */
  margin: 10px;
  border: 1px solid #ddd;
  padding: 10px;
  overflow-y: auto;
}

.table-container, .stats-container {
  max-width: 85%;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
}

.styled-table {
  width: 85%;
  border-collapse: collapse;
  font-size: 18px;
  text-align: left;
}

.styled-table thead {
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: #009879;
  color: #ffffff;
}

.styled-table th,
.styled-table td {
  padding: 12px 15px;
  border: 1px solid #dddddd;
}

.styled-table tbody tr:nth-of-type(even) {
  background-color: #f3f3f3;
}

.styled-table tbody tr:hover {
  background-color: #f1f1f1;
}

.fetch-button, .export-button {
  background-color: #009879;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 20px;
}

.load-more-button {
  background-color: #009879;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>