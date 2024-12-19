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
            <!-- Component 4: Main View -->
            <div class="main-view">
                <!-- Graph Display -->
                <v-chart :option="chartOptions" :key="refreshKey"></v-chart>
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
import StatisticsDropdown from "../components/StatisticsDropdown.vue";
import ExportConfig from "../components/ExportConfig.vue";
import ExportTableStats from "../components/ExportTableStats.vue";
import axios from 'axios';
import Multiselect from "vue-multiselect";
import { use } from 'echarts/core';
import { LineChart, ScatterChart, BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent, DataZoomComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';

use([LineChart, BarChart, ScatterChart, GridComponent, TooltipComponent, TitleComponent, DataZoomComponent, LegendComponent, CanvasRenderer]);


export default {
    name: "Graph",
    components: {
        DatabaseDropdown,
        ColumnDropdown,
        Selection,
        IntervalDropdown,
        StatisticsDropdown,
        ExportConfig,
        ExportTableStats,
        Multiselect,
        VChart,
    },
    data() {
        return {
            stats: [],
            statsColumns: [],
            data: [],
            ID: [],
            refreshKey: 0,
        };
    },
    watch: {
        selectedColumns() {
            this.ID = this.selectedColumns.filter((column) => column.includes('ID')).join("");
        },
    },
    computed: {
        ...mapState(["selectedDbsTables", "selectedColumns", "multiGraphType", "currentZoomStart", "currentZoomEnd", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "graphType", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "updateExportOptions", "pushMessage", "clearMessages"]),
        columnNeedsSecondaryAxis(column) {
            // Adjust logic based on actual data thresholds
            return this.data.some(row => row[column] > 100);
        },
        heightVar() {
            // Set the height based on the environment
            const isTauri = window.isTauri !== undefined;
            return isTauri ? "calc(100vh - 14vh)" : "calc(100vh - 16vh)";
        },
        getTitle() {
            // Set the title based on the first three letters of selected columns names
            return this.selectedColumns.length ? this.selectedColumns.filter(column => column !== this.dateType && column !== this.ID).map(col => col.slice(0, 3)).join(" - ") : "Graph";
        },
        getType(column) {
            // Use the Vuex state multiGraphType, which updates dynamically
            if (this.multiGraphType?.length > 0) {
                const multiGraph = this.multiGraphType.find(col => col.name === column);
                if (multiGraph) {
                    return multiGraph.type;
                }
            }
            // Handle cases where graphType contains a dash ('-')
            if (this.graphType.includes('-')) {
                return this.graphType.split('-')[0];
            }
            return this.graphType;
        },
        // Fetch data from the API
        async fetchData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/get_data`, {
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
                this.refreshKey += 1;

                this.$nextTick(() => {
                    this.pushMessage({ message: `Graph Loaded ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'success' });
                });

                this.pushMessage({ message: `Graph Loading ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'info' });
            } catch (error) {
                alert('Error fetching data: ' + error.message);
            }
        },
        // Export data to a file
        async exportData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}/api/export_data`, {
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
                        graph_type: this.graphType,
                        multi_graph_type: JSON.stringify(this.multiGraphType),
                    }
                });
                if (response.data.error) {
                    alert('Error fetching data:' + response.data.error);
                    return;
                }
                this.pushMessage({ message: `Exported ${this.exportColumns.length} columns x ${this.data.length} rows`, type: 'info' });
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