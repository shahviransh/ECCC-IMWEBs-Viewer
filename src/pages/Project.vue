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
            <TableStatsDisplay :data="data" :stats="stats" :statsColumns="statsColumns" :selectedColumns="selectedColumns" :ID="ID" :rowLimit="rowLimit" />
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import DatabaseDropdown from "../components/DatabaseDropdown.vue";
import ColumnDropdown from "../components/ColumnDropdown.vue";
import Selection from "../components/Selection.vue";
import IntervalDropdown from "../components/IntervalDropdown.vue";
import StatisticsDropdown from "../components/StatisticsDropdown.vue";
import ExportConfig from "../components/ExportConfig.vue";
import ExportTableStats from "../components/ExportTableStats.vue";
import TableStatsDisplay from "../components/TableStatsDisplay.vue";
import axios from 'axios';

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
        TableStatsDisplay,
    },
    data() {
        return {
            stats: [],
            statsColumns: [],
            data: [],
            ID: '',
            rowLimit: 100,
        };
    },
    computed: {
        ...mapState(["selectedDbsTables", "selectedColumns", "allSelectedColumns", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "updateExportOptions", "updateAllSelectedColumns", "pushMessage", "clearMessages"]),
        heightVar() {
            // Set the height based on the environment
            const isTauri = window.isTauri !== undefined;
            return isTauri ? "calc(100vh - 14vh)" : "calc(100vh - 16vh)";
        },
        // Fetch data from the API
        async fetchData() {
            try {
                // Choose all the columns if they are not selected
                if (this.selectedColumns.length === 0) {
                    this.updateSelectedColumns("All");
                    this.updateAllSelectedColumns(true);
                }

                // Fetch the data for the map
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/get_data`, {
                    params: {
                        db_tables: JSON.stringify(this.selectedDbsTables),
                        columns: JSON.stringify(this.allSelectedColumns ? "All" : this.selectedColumns.filter((column) => column !== 'Season')),
                        id: JSON.stringify(this.selectedIds),
                        start_date: this.dateRange.start,
                        end_date: this.dateRange.end,
                        date_type: this.dateType,
                        interval: this.selectedInterval,
                        statistics: JSON.stringify(this.selectedStatistics),
                        method: JSON.stringify(this.selectedMethod),
                    }
                });
                if (this.selectedInterval === 'seasonally' && !this.selectedMethod.includes('Equal') && !this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.concat(['Season']));
                } else if (this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.filter((column) => column !== 'Season'));
                }
                this.data = response.data.data;
                this.stats = response.data.stats;
                this.statsColumns = response.data.statsColumns;
                this.ID = this.selectedColumns.find((column) => column.includes('ID'));
                if (response.data.error) {
                    alert('Error fetching data: ', response.data.error);
                    return;
                } else {
                    // Wait until the table has rendered, then trigger messages
                    this.$nextTick(() => {
                        this.pushMessage({ message: `Fetched ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'success' });
                        this.pushMessage({ message: `Loaded ${this.rowLimit} rows`, type: 'success' });
                        if (this.statsColumns.length > 0) {
                            this.pushMessage({ message: `Fetched ${this.statsColumns.length} statistics columns for ${this.selectedMethod || this.selectedStatistics}`, type: 'success' });
                        }
                    });
                }
            } catch (error) {
                console.error('Error fetching data: ',  error.message);
            }
        },
        // Export data to a file
        async exportData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/export_data`, {
                    params: {
                        db_tables: JSON.stringify(this.selectedDbsTables),
                        columns: JSON.stringify(this.allSelectedColumns ? "All" : this.exportColumns.filter((column) => column !== 'Season')),
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
                    alert('Error fetching data: ', response.data.error);
                    return;
                }
                else { this.pushMessage({ message: `Exported ${this.exportColumns.length} columns x ${this.data.length} rows`, type: 'success' }); }
                if (this.selectedInterval === 'seasonally' && !this.selectedMethod.includes('Equal') && !this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.concat(['Season']));
                } else if (this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.filter((column) => column !== 'Season'));
                }
            } catch (error) {
                console.error('Error exporting data: ',  error.message);
            }
        },
    },
};
</script>
<style src="../assets/pages.css"></style>