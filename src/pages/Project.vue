<template>
    <!-- Main Content -->
    <div :class="[theme, 'content']" :style="{ height: heightVar() }">

        <!-- Component 1: Folder Navigation -->
        <div class="folder-navigation">
            <DatabaseDropdown />
        </div>

        <!-- Component 2: Column Navigation -->
        <div class="column-navigation">
            <ColumnDropdown :selectedTable="selectedTable" />
        </div>
        <div class="right-panel">
            <!-- Component 3: Selection, Interval, Aggregation, and Export Config -->
            <div class="settings-panel">
                <Selection />
                <IntervalDropdown />
                <span>
                    <StatisticsDropdown />
                    <AggregationMethod />
                </span>
                <ExportConfig />
                <span>
                    <div class="export-field">
                        <label for="export-stats">Export Table and/or Stats:</label>
                        <Multiselect v-model="selectedOptions" :options="filteredExportOptions" :multiple="true"
                            :close-on-select="false" :clear-on-select="false" :preserve-search="true"
                            placeholder="Select" @update:modelValue="onOptionsChange">
                        </Multiselect>
                    </div>
                    <button @click="fetchData">Fetch Data</button>
                    <button @click="exportData">Export Data</button>
                </span>
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
import DatabaseDropdown from "../components/DatabaseDropdown.vue";
import ColumnDropdown from "../components/ColumnDropdown.vue";
import Selection from "../components/Selection.vue";
import IntervalDropdown from "../components/IntervalDropdown.vue";
import AggregationMethod from "../components/AggregationMethod.vue";
import StatisticsDropdown from "../components/StatisticsDropdown.vue";
import ExportConfig from "../components/ExportConfig.vue";
import axios from 'axios';
import Multiselect from "vue-multiselect";

export default {
    name: "Project",
    components: {
        DatabaseDropdown,
        ColumnDropdown,
        Selection,
        IntervalDropdown,
        AggregationMethod,
        StatisticsDropdown,
        ExportConfig,
        Multiselect,
    },
    data() {
        return {
            stats: [],
            statsColumns: [],
            visibleData: [],
            rowLimit: 100,
            canLoadMore: true,
            data: [],
            selectedOptions: [],
        };
    },
    computed: {
        filteredExportOptions() {
            // Conditionally include "Stats" based on your original condition
            return this.selectedStatistics.includes('None') === this.selectedMethod.includes('Equal')
                ? ['Table']
                : ['Table', 'Stats'];
        },
        ...mapState(["selectedDb", "selectedTable", "selectedColumns", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "updateExportOptions"]),
        heightVar() {
            // Set the height based on the environment
            const isTauri = window.isTauri !== undefined;
            return isTauri ? 'calc(100vh - 14vh)' : 'calc(100vh - 16vh)';
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
        onOptionsChange(value) {
            this.selectedOptions = value;
            this.updateExportOptions({
                table: this.selectedOptions.includes('Table'),
                stats: this.selectedOptions.includes('Stats')
            });
        },
        async fetchData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/get_data`, {
                    params: {
                        db_path: this.selectedDb,
                        table_name: this.selectedTable,
                        columns: this.selectedColumns.filter((column) => column !== 'Season').join(","),
                        id: this.selectedIds.join(","),
                        start_date: this.dateRange.start,
                        end_date: this.dateRange.end,
                        date_type: this.dateType,
                        interval: this.selectedInterval,
                        statistics: this.selectedStatistics.join(","),
                        method: this.selectedMethod.join(","),
                    }
                });
                if (response.data.error) {
                    alert('Error fetching data:' + response.data.error);
                    return;
                }
                if (this.selectedInterval === 'seasonally' && !this.selectedMethod.includes('Equal') && !this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.concat(['Season']));
                } else {
                    this.updateSelectedColumns(this.selectedColumns.filter((column) => column !== 'Season'));
                }
                this.data = response.data.data;
                this.stats = response.data.stats;
                this.statsColumns = response.data.statsColumns;
                this.loadInitialRows();
            } catch (error) {
                alert('Error fetching data: ' + error.message);
            }
        },
        async exportData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/export_data`, {
                    params: {
                        db_path: this.selectedDb,
                        table_name: this.selectedTable,
                        columns: this.exportColumns.filter((column) => column !== 'Season').join(","),
                        id: this.exportIds.join(","),
                        start_date: this.exportDate.start,
                        end_date: this.exportDate.end,
                        date_type: this.exportDateType,
                        interval: this.exportInterval,
                        statistics: this.selectedStatistics.join(","),
                        method: this.selectedMethod.join(","),
                        date_type: this.dateType,
                        export_path: this.exportPath,
                        export_filename: this.exportFilename,
                        export_format: this.exportFormat,
                        options: this.exportOptions,
                    }
                });
                if (response.data.error) {
                    alert('Error fetching data:' + response.data.error);
                    return;
                }
                if (this.selectedInterval === 'seasonally' && !this.selectedMethod.includes('Equal') && !this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.concat(['Season']));
                } else {
                    this.updateSelectedColumns(this.selectedColumns.filter((column) => column !== 'Season'));
                }
            } catch (error) {
                alert('Error exporting data: ' + error.message);
            }
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style scoped>
/* Theme variables */
.light {
    --background-color: #ffffff;
    --text-color: #000000;
    --border-color: #ddd;
    --secondary-bg-color: #f3f3f3;
    --hover-bg-color: #f1f1f1;
    --table-header-bg: #9e3203;
    --table-header-text: #ffffff;
    --button-bg: linear-gradient(to bottom right, #8B5CF6, #3B82F6);
    /* from-purple-600 to-blue-500 */
    --button-text: #1F2937;
    --top-bar-bg: #b85b14;
    --top-bar-text: #fff;
    --taskbar-bg: #35495e;
    --taskbar-text: #fff;
    --active-bg: #009879;
}

.dark {
    --background-color: #121212;
    --text-color: #e0e0e0;
    --border-color: #444;
    --secondary-bg-color: #333;
    --hover-bg-color: #555;
    --table-header-bg: #444;
    --table-header-text: #e0e0e0;
    --button-bg: #333;
    --button-text: #e0e0e0;
    --top-bar-bg: #1e1e1e;
    --top-bar-text: #e0e0e0;
    --taskbar-bg: #2d2d2d;
    --taskbar-text: #cfcfcf;
    --active-bg: #5a5a5a;
}

:root {
    --top-bar-height: 14vh;
    --task-bar-height: 0;
}

body,
html {
    margin: 0;
    padding: 0;
    height: 100%;
    /* Ensure no scroll at the global level */
    background-color: var(--background-color);
    color: var(--text-color);
    overflow: hidden;
}

.content {
    display: flex;
    flex-direction: row;
    /* Adjust to the viewport, minus top bar and taskbar */
    overflow: hidden;
}

.multiselect {
    /* Set the desired width */
    font-size: 14px;
}

.export-field {
    display: flex;
    flex-direction: column;
    cursor: pointer;
}

label {
    font-weight: 600;
    font-size: 14px;
    color: #333;
    margin-bottom: 5px;
}

.folder-navigation,
.column-navigation,
.settings-panel,
.main-view,
.table-container,
.stats-container {
    background-color: var(--background-color);
    border: 1px solid var(--border-color);
    color: var(--text-color);
}

.folder-navigation {
    display: flex;
    flex-direction: column;
    width: 20%;
    /* Takes 1/4 of the horizontal space */
    height: calc(100% - 3%);
    margin: 0;
    padding: 10px;
    /* Takes 1/4 of the vertical space */
    overflow: auto;
}

.column-navigation {
    margin: 0;
    padding: 0px;
    width: 15%;
    height: 100%;
    flex-direction: column;
}

/* Right Panel: Settings Panel and Main View */
.right-panel {
    display: flex;
    flex-direction: column;
    width: 80%;
    height: 100%;
}

.settings-panel {
    width: 99%;
    /* Takes 2/4 of the horizontal space */
    height: 30%;
    /* Ensure full height */
    margin: 0px;
    padding: 5px;
    display: flex;
    flex-direction: row;
    justify-content: left;
    gap: 5px;
}

.main-view {
    width: 99%;
    /* Takes 2/4 of the horizontal space */
    height: 75%;
    /* Ensure full height */
    margin: 0px;
    padding: 5px;
    overflow: auto;
}

.table-container,
.stats-container {
    max-width: 100%;
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #ddd;
}

.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    text-align: left;
}

.styled-table thead {
    position: sticky;
    top: 0;
    z-index: 2;
    background-color: var(--table-header-bg);
    color: var(--table-header-text);
}

.styled-table th,
.styled-table td {
    padding: 12px 15px;
    border: 1px solid var(--border-color);
}

.styled-table tbody tr:nth-of-type(even) {
    background-color: var(--secondary-bg-color);
}

.styled-table tbody tr:hover {
    background-color: var(--hover-bg-color);
}

button {
    background-color: var(--button-bg);
    color: var(--button-text);
    padding: 0.2rem;
    margin-bottom: 0.5rem;
    margin-inline-end: 0.2rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background-color 0.3s ease, color 0.3s ease;
}

button:hover {
    background-color: var(--hover-bg-color);
}

button:focus {
    outline: none;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5);
    /* Optional, adjust for better contrast */
}
</style>