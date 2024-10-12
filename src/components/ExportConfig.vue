<template>
    <div class="export-container">
        <div class="export-field">
            <label for="export-path" class="export-label">Export Path:</label>
            <input type="text" id="export-path" v-model="expPath" class="export-input" @change="onExportChange" />
        </div>

        <div class="export-field">
            <label for="export-name" class="export-label">Export Filename:</label>
            <input type="text" id="export-name" v-model="expFilename" class="export-input"
                @change="onExportFileChange" />
        </div>

        <div class="export-field">
            <label for="export-format" class="export-label">Export Format:</label>
            <select id="export-format" v-model="expFormat" class="export-select" @change="onExportFormatChange">
                <option value="csv">CSV</option>
                <option value="text">Text</option>
            </select>
        </div>
    </div>

    <div class="export-field">
        <label for="export-stats">Export Table and/or Stats</label>
        <Multiselect v-model="selectedOptions" :options="filteredExportOptions" :multiple="true"
            :close-on-select="false" :clear-on-select="false" :preserve-search="true"
            placeholder="Select Export Options" @update:modelValue="onOptionsChange">
        </Multiselect>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import Multiselect from 'vue-multiselect';

export default {
    data() {
        return {
            selectedOptions: [],
            exportOptions: [
                "Table",
                "Stats"
            ]
        };
    },
    components: { Multiselect },
    computed: {
        expPath: {
            get() {
                return this.exportPath;
            },
            set(value) {
                this.updateExportPath(value);
            },
        },
        expFilename: {
            get() {
                return this.exportFilename;
            },
            set(value) {
                this.updateExportFilename(value);
            },
        },
        expFormat: {
            get() {
                return this.exportFormat;
            },
            set(value) {
                this.updateExportFormat(value);
            },
        },
        filteredExportOptions() {
            // Conditionally include "Stats" based on your original condition
            return this.selectedStatistics.includes('None') === this.selectedMethod.includes('Equal')
                ? ['Table']
                : ['Table', 'Stats'];
        },
        ...mapState(['selectedStatistics', 'selectedMethod', 'exportPath', 'exportFilename', 'exportFormat']),
    },
    methods: {
        ...mapActions(["updateExportPath", "updateExportFilename", "updateExportFormat", "updateExportOptions"]),
        onOptionsChange(value) {
            this.selectedOptions = value;
            this.updateExportOptions({
                table: this.selectedOptions.includes('Table'),
                stats: this.selectedOptions.includes('Stats')
            });
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style scoped>
.multiselect__content-wrapper {
    z-index: 1000;
    /* or a higher value */
}

.export-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 20px;
    overflow: auto;
}

.export-field {
    display: flex;
    flex-direction: column;
    cursor: pointer;
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
