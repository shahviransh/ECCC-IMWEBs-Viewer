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
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    data() {
        return {
        };
    },
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
        ...mapState(['selectedStatistics', 'selectedMethod', 'exportPath', 'exportFilename', 'exportFormat']),
    },
    methods: {
        ...mapActions(["updateExportPath", "updateExportFilename", "updateExportFormat"]),
    },
};
</script>

<style scoped>
.export-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 20px;
    overflow: auto;
}

label {
    font-weight: 600;
    font-size: 14px;
    color: #333;
    margin-bottom: 5px;
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
