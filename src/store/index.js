import { createStore } from "vuex";
import axios from "axios";

const store = createStore({
  state: {
    selectedDbsTables: [],
    selectedColumns: [],
    selectedGeoFolder: null,
    selectedIds: [],
    dateRange: {
      start: null,
      end: null,
    },
    tooltipColumns: {},
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
    multiGraphType: [],
    exportOptions: { data: false, stats: false },
    defaultInterval: "",
    defaultStartDate: "",
    defaultEndDate: "",
    messages: [],
    xAxis: "",
    yAxis: [],
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

      // Remove the selected/export columns that are not in the new columns
      state.selectedColumns = state.selectedColumns.filter((column) =>
        columns.includes(column)
      );
      state.exportColumns = state.exportColumns.filter((column) =>
        columns.includes(column)
      );
    },
    SET_SELECTED_DB_TABLE_REMOVE(state, table) {
      state.selectedDbsTables = state.selectedDbsTables.filter(
        (t) => t.table !== table
      );
    },
    SET_TOOLTIP_COLUMNS(state, columns) {
      state.tooltipColumns = { ...columns };
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
    SET_DEFAULT_SELECTIONS(
      state,
      { defaultInterval, defaultStartDate, defaultEndDate }
    ) {
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
    SET_MULTI_GRAPH_TYPE(state, formats) {
      state.multiGraphType = formats;
    },
    SET_THEME(state, theme) {
      state.theme = theme;
    },
    SET_PAGE_TITLE(state, title) {
      state.pageTitle = title;
    },
    SET_SELECTED_DBS_TABLES(state, { db, table }) {
      if (
        !state.selectedDbsTables.some((t) => t.db === db && t.table === table)
      ) {
        state.selectedDbsTables.push({ db, table });
      }
      const temp = state.selectedDbsTables;
      state.selectedDbsTables = [...temp];
    },
    SET_SELECTED_GEO_FOLDER(state, folder) {
      state.selectedGeoFolder = folder;
    },
    SET_XAXIS(state, xAxis) {
      state.xAxis = xAxis;
    },
    SET_YAXIS(state, yAxis) {
      state.yAxis = yAxis;
      state.selectedColumns = [state.xAxis, ...yAxis];
      state.exportColumns = [...state.selectedColumns];
    },
    PUSH_MESSAGE(state, { message, type, duration }) {
      state.messages.push({
        text: message,
        type: type,
        timeLeft: duration,
        totalTime: duration,
      });
    },
    SLICE_MESSAGE(state, index) {
      state.messages.splice(index, 1);
    },
    CLEAR_MESSAGES(state) {
      state.messages = [];
    },
    SET_SELECTED_COLUMNS(state, columns) {
      state.selectedColumns = columns;
      state.exportColumns = columns;
      console.log(columns);
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
      const maxRetries = 5; // Maximum number of retry attempts
      const retryDelay = 2000; // Delay between retries in milliseconds

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/list_files`, {
            params: { folder_path: "Jenette_Creek_Watershed" },
          });
          if (response.data.error) {
            alert("Error fetching data: " + response.data.error);
            return;
          }
          commit("SET_DATABASES", response.data);
          return; // Exit the function if the request is successful
        } catch (error) {
          alert(
            `Attempt ${attempt} - Error fetching databases:`,
            error.message
          );
          if (attempt === maxRetries) {
            alert("Max retries reached. Failed to fetch databases.");
            throw error; // Re-throw the error after the last attempt
          }
          await new Promise((resolve) => setTimeout(resolve, retryDelay)); // Wait before retrying
        }
      }
    },
    async fetchTables({ commit }, db) {
      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/get_tables`, {
          params: { db_path: db },
        });
        if (response.data.error) {
          alert("Error fetching data: " + response.data.error);
          return;
        }
        commit("SET_TABLES", response.data);
      } catch (error) {
        alert("Error fetching tables: ", error.message);
      }
    },
    async fetchColumns({ commit }, dbTables) {
      try {
        // Fecth based on dbTables or selectedGeoFolder
        let response;
        if (typeof dbTables === "object") {
          // Fetch all columns for all tables selected
          response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/get_table_details`, {
            params: { db_tables: JSON.stringify(dbTables) },
          });
        } 
        // else {
        //   // Fetch all columns for the selected folder
        //   response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/get_dbf_details`, {
        //     params: { directory: JSON.stringify(this.dbTables) },
        //   });
        // }
        if (response.data.error) {
          alert("Error fetching data: " + response.data.error);
          return;
        }
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
        commit("SET_DEFAULT_SELECTIONS", {
          defaultInterval: response.data.interval,
          defaultStartDate: response.data.start_date,
          defaultEndDate: response.data.end_date,
        });
        commit("SET_TOOLTIP_COLUMNS", response.data.global_columns);
      } catch (error) {
        alert("Error fetching columns: ", error.message);
      }
    },
    // Add similar actions for other components
    updateSelectedDbsTables({ commit }, { db, table }) {
      commit("SET_SELECTED_DBS_TABLES", { db, table });
    },
    updateSelectedGeoFolder({ commit }, folder) {
      commit("SET_SELECTED_GEO_FOLDER", folder);
    },
    updateTheme({ commit }, theme) {
      commit("SET_THEME", theme);
    },
    removeSelectedDbTable({ commit }, table) {
      commit("SET_SELECTED_DB_TABLE_REMOVE", table);
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
    updateYAxis({ commit }, yAxis) {
      commit("SET_YAXIS", yAxis);
    },
    updateXAxis({ commit }, xAxis) {
      commit("SET_XAXIS", xAxis);
    },
    pushMessage({ commit }, { message, type, duration = 1000 }) {
      commit("PUSH_MESSAGE", { message, type, duration });
    },
    sliceMessage({ commit }, index) {
      commit("SLICE_MESSAGE", index);
    },
    clearMessages({ commit }) {
      commit("CLEAR_MESSAGES");
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
    updateMultiGraphType({ commit }, formats) {
      commit("SET_MULTI_GRAPH_TYPE", formats);
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
