import { createStore } from "vuex";
import axios from "axios";

const store = createStore({
  state: {
    selectedDb: null,
    selectedTable: null,
    selectedColumns: [],
    selectedIds: [],
    dateRange: {
      start: null,
      end: null,
    },
    theme: "light",
    pageTitle: "",
    databases: [],
    tables: [],
    columns: [],
    ids: [],
    currentZoomStart: 0,
    currentZoomEnd: 100,
    exportColumns: [],
    exportIds: [],
    exportDate: {
      start: null,
      end: null,
    },
    dateType: null,
    exportDateType: null,
    selectedMethod: ["Equal"],
    selectedStatistics: ["None"],
    selectedInterval: "daily",
    exportInterval: "daily",
    exportPath: "dataExport",
    exportFilename: "exported_data",
    exportFormat: "csv",
    graphType: "scatter",
    exportOptions: { data: false, stats: false },
    defaultInterval: "",
    defaultStartDate: "",
    defaultEndDate: "",
  },
  mutations: {
    SET_DATABASES(state, databases) {
      state.databases = databases;
    },
    SET_TABLES(state, tables) {
      state.tables = tables;
    },
    SET_COLUMNS(state, { columns }) {
      state.columns = columns;
    },
    SET_OPTIONS(
      state,
      { ids, dateRange, dateType, exportDate, exportDateType }
    ) {
      state.ids = ids;
      state.dateRange = dateRange;
      state.dateType = dateType;
      state.exportDate = exportDate;
      state.exportDateType = exportDateType;
    },
    SET_DEFAULT_SELECTIONS(state, {defaultInterval, defaultStartDate, defaultEndDate}) {
      state.defaultInterval = defaultInterval;
      state.defaultStartDate = defaultStartDate;
      state.defaultEndDate = defaultEndDate;
    },
    SET_CURRENT_ZOOM(state, { start, end }) {
      state.currentZoomStart = start;
      state.currentZoomEnd = end;
    },
    SET_GRAPH_TYPE(state, format) {
      state.graphType = format;
    },
    SET_THEME(state, theme) {
      state.theme = theme;
    },
    SET_PAGE_TITLE(state, title) {
      state.pageTitle = title;
    },
    SET_SELECTED_DB(state, db) {
      state.selectedDb = db;
    },
    SET_SELECTED_TABLE(state, table) {
      state.selectedTable = table;
    },
    SET_SELECTED_COLUMNS(state, columns) {
      state.selectedColumns = columns;
      state.exportColumns = columns;
    },
    SET_SELECTED_IDS(state, ids) {
      state.selectedIds = ids;
    },
    SET_SELECTED_DATE(state, { start, end }) {
      if (start) {
        state.dateRange.start = start;
      }
      if (end) {
        state.dateRange.end = end;
      }
    },
    SET_EXPORT_COLUMNS(state, columns) {
      state.exportColumns = columns;
    },
    SET_EXPORT_IDS(state, ids) {
      state.exportIds = ids;
    },
    SET_EXPORT_DATE(state, { start, end }) {
      if (start) {
        state.exportDate.start = start;
      }
      if (end) {
        state.exportDate.end = end;
      }
    },
    SET_DATE_TYPE(state, type) {
      state.dateType = type;
    },
    SET_EXPORT_DATE_TYPE(state, type) {
      state.exportDateType = type;
    },
    SET_SELECTED_METHOD(state, method) {
      state.selectedMethod = method;
    },
    SET_SELECTED_STATISTICS(state, statistics) {
      state.selectedStatistics = statistics;
    },
    SET_SELECTED_INTERVAL(state, interval) {
      state.selectedInterval = interval;
    },
    SET_EXPORT_INTERVAL(state, interval) {
      state.exportInterval = interval;
    },
    SET_EXPORT_PATH(state, path) {
      state.exportPath = path;
    },
    SET_EXPORT_FILENAME(state, filename) {
      state.exportFilename = filename;
    },
    SET_EXPORT_FORMAT(state, format) {
      state.exportFormat = format;
    },
    SET_EXPORT_OPTIONS(state, options) {
      state.exportOptions = options;
    },
  },
  actions: {
    async fetchDatabases({ commit }) {
      const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL;
      const maxRetries = 5; // Maximum number of retry attempts
      const retryDelay = 2000; // Delay between retries in milliseconds
    
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          const response = await axios.get(`${apiBaseUrl}/api/list_files`, {
            params: { folder_path: "Jenette_Creek_Watershed" },
          });
          commit("SET_DATABASES", response.data);
          return; // Exit the function if the request is successful
        } catch (error) {
          alert(`Attempt ${attempt} - Error fetching databases:`, error.message);
          if (attempt === maxRetries) {
            alert("Max retries reached. Failed to fetch databases.");
            throw error; // Re-throw the error after the last attempt
          }
          await new Promise(resolve => setTimeout(resolve, retryDelay)); // Wait before retrying
        }
      }
    },    
    async fetchTables({ commit }, db) {
      const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL;
      try {
        const response = await axios.get(`${apiBaseUrl}/api/get_tables`, {
          params: { db_path: db },
        });
        commit("SET_TABLES", response.data);
      } catch (error) {
        alert("Error fetching tables:", error.message);
      }
    },
    async fetchColumns({ commit }, { db, table }) {
      const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL;
      try {
        const response = await axios.get(
          `${apiBaseUrl}/api/get_table_details`,
          {
            params: { db_path: db, table_name: table },
          }
        );
        commit("SET_COLUMNS", {
          columns: response.data.columns,
        });
        commit("SET_OPTIONS", {
          ids: response.data.ids,
          dateRange: {
            start: response.data.start_date,
            end: response.data.end_date,
          },
          dateType: response.data.date_type,
          exportDate: {
            start: response.data.start_date,
            end: response.data.end_date,
          },
          exportDateType: response.data.date_type,
          selectedInterval: response.data.interval,
          exportInterval: response.data.interval,
        });
        commit("SET_DEFAULT_SELECTIONS", {defaultInterval: response.data.interval, defaultStartDate: response.data.start_date, defaultEndDate: response.data.end_date});
      } catch (error) {
        alert("Error fetching columns:", error.message);
      }
    },
    // Add similar actions for other components
    updateSelectedDb({ commit }, db) {
      commit("SET_SELECTED_DB", db);
    },
    updateTheme({ commit }, theme) {
      commit("SET_THEME", theme);
    },
    updateSelectedTable({ commit }, table) {
      commit("SET_SELECTED_TABLE", table);
    },
    updatePageTitle({ commit }, title) {
      commit("SET_PAGE_TITLE", title);
    },
    updateSelectedColumns({ commit }, columns) {
      commit("SET_SELECTED_COLUMNS", columns);
    },
    updateSelectedIds({ commit }, ids) {
      commit("SET_SELECTED_IDS", ids);
    },
    updateSelectedDateStart({ commit }, start) {
      commit("SET_SELECTED_DATE", { start: start, end: null });
    },
    updateSelectedDateEnd({ commit }, end) {
      commit("SET_SELECTED_DATE", { start: null, end: end });
    },
    updateExportColumns({ commit }, columns) {
      commit("SET_EXPORT_COLUMNS", columns);
    },
    updateExportIds({ commit }, ids) {
      commit("SET_EXPORT_IDS", ids);
    },
    updateExportDateStart({ commit }, start) {
      commit("SET_EXPORT_DATE", { start: start, end: null });
    },
    updateExportDateEnd({ commit }, end) {
      commit("SET_EXPORT_DATE", { start: null, end: end });
    },
    updateGraphType({ commit }, format) {
      commit("SET_GRAPH_TYPE", format);
    },
    updateCurrentZoom({ commit }, { start, end }) {
      commit("SET_CURRENT_ZOOM", { start: start, end: end });
    },
    updateDateType({ commit }, type) {
      commit("SET_DATE_TYPE", type);
    },
    updateExportDateType({ commit }, type) {
      commit("SET_EXPORT_DATE_TYPE", type);
    },
    updateSelectedMethod({ commit }, method) {
      commit("SET_SELECTED_METHOD", method);
    },
    updateSelectedStatistics({ commit }, statistics) {
      commit("SET_SELECTED_STATISTICS", statistics);
    },
    updateSelectedInterval({ commit }, interval) {
      commit("SET_SELECTED_INTERVAL", interval);
    },
    updateExportInterval({ commit }, interval) {
      commit("SET_EXPORT_INTERVAL", interval);
    },
    updateExportPath({ commit }, path) {
      commit("SET_EXPORT_PATH", path);
    },
    updateExportFilename({ commit }, filename) {
      commit("SET_EXPORT_FILENAME", filename);
    },
    updateExportFormat({ commit }, format) {
      commit("SET_EXPORT_FORMAT", format);
    },
    updateExportOptions({ commit }, options) {
      commit("SET_EXPORT_OPTIONS", options);
    },
  },
});

export default store;
