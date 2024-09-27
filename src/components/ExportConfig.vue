<template>
    <div class="export-container">
        <div class="export-field">
            <label for="export-path" class="export-label">Export Path:</label>
            <input type="text" id="export-path" v-model="exportPath" class="export-input" />
        </div>

        <div class="export-field">
            <label for="export-name" class="export-label">Export Filename:</label>
            <input type="text" id="export-name" v-model="exportFilename" class="export-input" />
        </div>

        <div class="export-field">
            <label for="export-format" class="export-label">Export Format:</label>
            <select id="export-format" v-model="exportFormat" class="export-select">
                <option value="csv">CSV</option>
                <option value="text">Text</option>
            </select>
        </div>
        <div class="export-field">
            <label for="export-stats">Export Table and/or Stats</label>
            <select id="export-stats" v-model="selectedOptions" multiple class="export-select" @change="onOptionsChange()">
                <option value="table">Table</option>
                <option v-if="!selectedStatistics.includes('None') != !intervalStats.includes('Equal')" value="stats">Stats</option>
            </select>
        </div>
        {{ onExportChange() }}
    </div>
</template>

<script>
import axios from "axios";
export default {
    props: {
        selectedStatistics: Array,
        intervalStats: Array,
    },
    data() {
        return {
            exportPath: "dataExport",
            exportFilename: "exported_data",
            exportFormat: "csv",
            selectedOptions: [],
            exportOptions: { data: false, stats: false },
        };
    },
    methods: {
        onExportChange() {
            this.$emit("export-config-changed", {
                path: this.exportPath,
                filename: this.exportFilename,
                format: this.exportFormat,
                options: this.exportOptions,
            });
        },
        onOptionsChange() {
            this.exportOptions = {
                data: this.selectedOptions.includes("table"),
                stats: this.selectedOptions.includes("stats"),
            };
        },
    },
};
</script>

<style scoped>
.export-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 20px;
}

.export-field {
    display: flex;
    flex-direction: column;
}

.export-label {
    font-weight: bold;
    font-size: 14px;
    color: #333;
    margin-bottom: 5px;
}

.export-input {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
    transition: border-color 0.3s ease-in-out;
}

.export-input:focus {
    border-color: #555;
    outline: none;
}

.export-select {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    width: 100%;
}

.export-select:focus {
    border-color: #555;
    outline: none;
}

.export-container select,
.export-container input {
    max-width: 300px;
    /* Limit width to make it look consistent */
}
</style>