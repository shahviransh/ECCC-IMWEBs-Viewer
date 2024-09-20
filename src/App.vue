<template>
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

  <div class="table-container">
    <table class="styled-table">
      <thead>
        <tr>
          <th v-for="column in selectedColumns" :key="column">{{ column }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in data" :key="index">
          <td v-for="column in selectedColumns" :key="column">{{ row[column] }}</td>
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
      selectedDb: '',          // Define selectedDb
      selectedTable: '',       // Define selectedTable
      selectedColumns: [],    // Define selectedColumns
      selectedIds: [],        // Define selectedIds
      dateRange: {}, // Define dateRange
      selectedInterval: 'daily', // Define selectedInterval
      selectedStatistics: ['None'], // Define selectedStatistics
      aggregationMethod: ['Equal'], // Define aggregationMethods
      exportColumns: [], // Define exportColumns
      exportIds: [], // Define exportIds
      exportDate: {}, // Define exportDate
      exportInterval: 'daily', // Define exportInterval
      exportConfig: {         // Define exportConfig
        path: '',
        filename: '',
        format: 'csv',
      },
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
      this.selectedColumns.unshift('Statistics');
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
        this.data = response.data;
      } catch (error) {
        console.error('Error fetching data:', error);
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
  overflow-x: auto;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-size: 18px;
  text-align: left;
}

.styled-table thead tr {
  background-color: #009879;
  color: #ffffff;
  text-align: left;
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

.styled-table tbody tr:last-of-type {
  border-bottom: 2px solid #009879;
}

.styled-table tbody tr:hover {
  background-color: #f1f1f1;
  cursor: pointer;
}

/* Button styling */
.fetch-button {
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

.fetch-button:hover {
  background-color: #007f67;
}

/* Button styling */
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

.export-button:hover {
  background-color: #007f67;
}
</style>
