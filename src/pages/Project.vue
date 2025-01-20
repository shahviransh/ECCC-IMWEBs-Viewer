<template>
    <!-- Main Content -->
    <div :class="[theme, 'content']" :style="{ height: heightVar() }">

        <!-- Component 1: Folder Navigation -->
        <div class="folder-navigation">
            <DatabaseDropdown />
        </div>

        <!-- Component 2: Column Navigation -->
        <div class="column-navigation">
            <ColumnDropdown :selectedDbsTables="selectedDbsTables" />
        </div>
        <div class="right-panel">
            <!-- Component 3: Selection, Interval, Aggregation, and Export Config -->
            <div class="settings-panel">
                <Selection />
                <IntervalDropdown />
                <StatisticsDropdown />
                <ExportConfig />
                <span>
                    <ExportTableStats />
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
import { nextTick } from "vue";
import DatabaseDropdown from "../components/DatabaseDropdown.vue";
import ColumnDropdown from "../components/ColumnDropdown.vue";
import Selection from "../components/Selection.vue";
import IntervalDropdown from "../components/IntervalDropdown.vue";
import StatisticsDropdown from "../components/StatisticsDropdown.vue";
import ExportConfig from "../components/ExportConfig.vue";
import ExportTableStats from "../components/ExportTableStats.vue";
import axios from 'axios';
import Multiselect from "vue-multiselect";

export default {
    name: "Project",
    components: {
        DatabaseDropdown,
        ColumnDropdown,
        Selection,
        IntervalDropdown,
        StatisticsDropdown,
        ExportConfig,
        ExportTableStats,
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
        };
    },
    computed: {
        ...mapState(["selectedDbsTables", "selectedColumns", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "updateExportOptions", "pushMessage", "clearMessages"]),
        heightVar() {
            // Set the height based on the environment
            const isTauri = window.isTauri !== undefined;
            return isTauri ? "calc(100vh - 14vh)" : "calc(100vh - 16vh)";
        },
        // Load initial rows when the data is loaded
        loadInitialRows() {
            this.visibleData = this.data.slice(0, this.rowLimit);
            this.canLoadMore = this.data.length > this.rowLimit;
        },
        // Load more rows when the load more button is clicked
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
        // Fetch data from the API
        async fetchData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/get_data`, {
                    params: {
                        db_tables: JSON.stringify(this.selectedDbsTables),
                        columns: JSON.stringify(this.selectedColumns.filter((column) => column !== 'Season')),
                        id: JSON.stringify(this.selectedIds),
                        start_date: this.dateRange.start,
                        end_date: this.dateRange.end,
                        date_type: this.dateType,
                        interval: this.selectedInterval,
                        statistics: JSON.stringify(this.selectedStatistics),
                        method: JSON.stringify(this.selectedMethod),
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
                this.pushMessage({ message: `Fetching ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'info' });
                this.loadInitialRows();

                // Wait until the table has rendered, then trigger messages
                this.$nextTick(() => {
                    this.pushMessage({ message: `Fetched ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'success' });
                    this.pushMessage({ message: `Loaded ${this.rowLimit} rows`, type: 'success' });
                    if (this.statsColumns.length > 0) {
                        this.pushMessage({ message: `Fetched ${this.statsColumns.length} statistics columns for ${this.selectedMethod || this.selectedStatistics}`, type: 'success' });
                    }
                });
            } catch (error) {
                alert('Error fetching data: ' + error.message);
            }
        },
        // Export data to a file
        async exportData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/export_data`, {
                    params: {
                        db_tables: JSON.stringify(this.selectedDbsTables),
                        columns: JSON.stringify(this.exportColumns.filter((column) => column !== 'Season')),
                        id: JSON.stringify(this.exportIds),
                        start_date: this.exportDate.start,
                        end_date: this.exportDate.end,
                        date_type: this.exportDateType,
                        interval: this.exportInterval,
                        statistics: JSON.stringify(this.selectedStatistics),
                        method: JSON.stringify(this.selectedMethod),
                        date_type: this.dateType,
                        export_path: this.exportPath,
                        export_filename: this.exportFilename,
                        export_format: this.exportFormat,
                        options: JSON.stringify(this.exportOptions),
                    }
                });
                if (response.data.error) {
                    alert('Error fetching data:' + response.data.error);
                    return;
                }
                this.pushMessage({ message: `Exported ${this.exportColumns.length} columns x ${this.data.length} rows`, type: 'success' });
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
<style src="../assets/pages.css"></style>