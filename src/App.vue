<template>
  <div>
    <!-- Existing UI components -->
    <button @click="shutdownServer">Shutdown Server</button>
    <div v-if="shutdownMessage">{{ shutdownMessage }}</div>
  </div>
  <div>
    <DatabaseDropdown @database-selected="onDatabaseSelected" />
    <TableDropdown :selectedDb="selectedDb" @table-selected="onTableSelected" />
    <ColumnDropdown :selectedDb="selectedDb" :selectedTable="selectedTable" @columns-selected="onColumnsSelected" @export-selected="onExportSelected" />
    <IntervalDropdown @interval-selected="onIntervalSelected" @export-interval-selected="onExportIntervalSelected" />
    <StatisticsDropdown @statistics-selected="onStatisticsSelected" />
    <AggregationMethod @method-selected="onMethodSelected" />
    <ExportConfig @export-config-changed="onExportConfigChanged" @export-data="exportData" />
    <button class="fetch-button" @click="fetchData">Fetch Data</button>
  </div>
  <div>
    <button class="export-button" @click="exportData">Export Data</button>
    <h4>Saved {{exportConfig.filename}} to {{ exportConfig.path }} as a {{ exportConfig.format }}</h4>
  </div>

  <!-- Table Container with Fixed Height and Scrollable Body -->
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
  <!-- Stats Container with Fixed Height and Scrollable Body -->
  <div class="table-container">
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
</template>

<script>
import DatabaseDropdown from './components/DatabaseDropdown.vue';
import TableDropdown from './components/TableDropdown.vue';
import ColumnDropdown from './components/ColumnDropdown.vue';
import IntervalDropdown from './components/IntervalDropdown.vue';
import StatisticsDropdown from './components/StatisticsDropdown.vue';
import AggregationMethod from './components/AggregationMethod.vue';
import ExportConfig from './components/ExportConfig.vue';
import axios from 'axios';

export default {
  components: {
    DatabaseDropdown,
    TableDropdown,
    ColumnDropdown,
    IntervalDropdown,
    StatisticsDropdown,
    AggregationMethod,
    ExportConfig,
  },
  data() {
    return {
      shutdownMessage: '',
      selectedDb: '',          // Define selectedDb
      selectedTable: '',       // Define selectedTable
      selectedColumns: [],    // Define selectedColumns
      selectedIds: [],        // Define selectedIds
      dateRange: {}, // Define dateRange
      selectedInterval: 'daily', // Define selectedInterval
      selectedStatistics: ['None'], // Define selectedStatistics
      aggregationMethod: ['Equal'], // Define aggregationMethods
      stats: [], // Define stats
      statsColumns: [], // Define statsColumns
      options: {}, // Define options
      exportColumns: [], // Define exportColumns
      exportIds: [], // Define exportIds
      exportDate: {}, // Define exportDate
      exportInterval: 'daily', // Define exportInterval
      exportConfig: {         // Define exportConfig
        path: '',
        filename: '',
        format: 'csv',
        options: {},
      },
      visibleData: [], // Data to be displayed
      rowLimit: 100, // Number of rows to load initially
      canLoadMore: true, // Controls visibility of the Load More button
      data: [],
      dateType: '',
      exportDateType: '',
    };
  },
  methods: {
    onDatabaseSelected(database) {
      this.selectedDb = database;
    },
    onTableSelected(table) {
      this.selectedTable = table;
    },
    onColumnsSelected(data) {
      this.selectedColumns = data.selectedColumns;
      this.selectedColumns = [...new Set(this.selectedColumns)];
      this.dateRange = data.selectedDate
      this.selectedIds = data.selectedIds;
      this.dateType = data.dateType;
    },
    onIntervalSelected(interval) {
      this.selectedInterval = interval;
    },
    onMethodSelected(method) {
      this.aggregationMethod = method;
    },
    onStatisticsSelected(statistics) {
      this.selectedStatistics = statistics;
    },
    onExportConfigChanged(config) {
      this.exportConfig = config;
    },
    onExportSelected(data) {
      this.exportColumns = data.selectedColumns;
      this.exportDate = data.selectedDate;
      this.exportIds = data.selectedIds;
      this.exportDateType = data.dateType;
    },
    onExportIntervalSelected(interval) {
      this.exportInterval = interval;
    },
    async shutdownServer() {
      try {
        const response = await axios.get('http://localhost:5000/shutdown');
        this.shutdownMessage = response.data;
      } catch (error) {
        console.error('Error shutting down server:', error);
      }
    },
    async fetchData() {
      // Implement data fetching logic based on selected options
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
            method: this.aggregationMethod.join(","),
          }
        });
        this.data = response.data.data;
        this.stats = response.data.stats;
        this.statsColumns = response.data.statsColumns;
        this.loadInitialRows(); // Load initial rows to visibleData
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
    loadInitialRows() {
      // Load the first 100 rows
      this.visibleData = this.data.slice(0, this.rowLimit);
      // Check if there's more data to load
      this.canLoadMore = this.data.length > this.rowLimit;
    },
    loadMoreRows() {
      const nextRowLimit = this.visibleData.length + this.rowLimit;
      const nextRows = this.data.slice(this.visibleData.length, nextRowLimit);
      // Append new rows to the visible data
      this.visibleData = [...this.visibleData, ...nextRows];
      // Check if there are more rows to load
      if (this.visibleData.length >= this.data.length) {
        this.canLoadMore = false; // Hide "Load More" button if all data is loaded
      }
    },
    async exportData() {
      // Add export logic here
      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/export_data`, {
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
            method: this.aggregationMethod.join(","),
            export_path: this.exportConfig.path,
            export_filename: this.exportConfig.filename,
            export_format: this.exportConfig.format,
            options: this.exportConfig.options,
          }
        });
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }
  },
};
</script>

<style scoped>
/* Styling for the table */
.table-container {
  max-width: 100%;
  max-height: 300px; /* Set a fixed height for the table container */
  overflow-y: auto; /* Enable vertical scroll if the content exceeds the height */
  border: 1px solid #ddd;
  position: relative;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 18px;
  text-align: left;
}

/* Keep the header fixed */
.styled-table thead {
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: #009879; /* Header background color */
  color: #ffffff; /* Header text color */
}

.styled-table th,
.styled-table td {
  padding: 12px 15px;
  border: 1px solid #dddddd;
}

.styled-table tbody tr {
  border-bottom: 1px solid #dddddd;
}

.styled-table tbody tr:nth-of-type(even) {
  background-color: #f3f3f3;
}

.styled-table tbody tr:hover {
  background-color: #f1f1f1;
  cursor: pointer;
}

/* Button styling */
.fetch-button,
.export-button {
  background-color: #009879;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 20px;
  font-size: 16px;
  transition: background-color 0.3s ease-in-out;
}

.fetch-button:hover,
.export-button:hover {
  background-color: #007f67;
}

/* Load More Button Styling */
.load-more-container {
  text-align: center;
  padding: 10px 0;
}

.load-more-button {
  background-color: #009879;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease-in-out;
}

.load-more-button:hover {
  background-color: #007f67;
}
</style>
