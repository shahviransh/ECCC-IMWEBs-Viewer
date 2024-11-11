<template>
    <div class="export-container">
        <div class="export-field">
            <label for="export-path" class="export-label">Export Path:</label>
            <input type="text" id="export-path" v-model="expPath" class="export-input" />
        </div>

        <div class="export-field">
            <label for="export-name" class="export-label">Export Filename:</label>
            <input type="text" id="export-name" v-model="expFilename" class="export-input"
                @change="onExportFileChange" />
        </div>

        <div class="export-field">
            <label for="export-format" class="export-label">Export Format:</label>
            <select id="export-format" v-model="expFormat" class="export-select">
                <option value="csv">CSV</option>
                <option value="txt">Text</option>
                <!-- Conditional Graph Export Options -->
                <template v-if="pageTitle === 'Graph'">
                    <option value="xlsx">Graph In Excel</option>
                    <option value="png">Graph As PNG</option>
                    <option value="jpg">Graph As JPG</option>
                    <option value="jpeg">Graph As JPEG</option>
                    <option value="svg">Graph As SVG</option>
                    <option value="pdf">Graph As PDF</option>
                </template>
            </select>
        </div>
        <div v-if="pageTitle === 'Graph'" class="export-field">
            <label for="graph-type" class="export-label">Graph Type:</label>
            <select id="graph-type" v-model="graType" class="export-select">
                <option value="bar">Bar</option>
                <option value="line">Line</option>
                <option value="scatter">Scatter</option>
            </select>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import DOMPurify from 'dompurify';

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
                this.updateExportPath(DOMPurify.sanitize(value));
            },
        },
        expFilename: {
            get() {
                return this.exportFilename;
            },
            set(value) {
                this.updateExportFilename(DOMPurify.sanitize(value));
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
        graType: {
            get() {
                return this.graphType;
            },
            set(value) {
                this.updateGraphType(value);
            },
        },
        ...mapState(['exportPath', 'exportFilename', 'exportFormat', "pageTitle", "graphType"]),
    },
    methods: {
        ...mapActions(["updateExportPath", "updateExportFilename", "updateExportFormat", "updateGraphType"]),
    },
};
</script>

<style scoped>
.export-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin: 0px 0px;
    padding: 5px;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    background-color: antiquewhite;
    overflow-y: auto;
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
    padding: 5px;
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
    padding: 5px;
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
