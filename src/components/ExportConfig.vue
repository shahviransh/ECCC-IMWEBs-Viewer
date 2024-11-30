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
                <option value="bar-line">Bar & Line</option>
                <option value="line-scatter">Line & Scatter</option>
                <option value="scatter-bar">Scatter & Bar</option>
            </select>
            <!-- Conditional Multiselects -->
            <div v-if="['bar-line', 'line-scatter', 'scatter-bar'].includes(graType)" class="export-field">
                <label for="multiselect1" class="export-label">Select Columns for {{ this.mapping[0] }}:</label>
                <Multiselect id="multiselect1" v-model="selectedColumns1" :options="filteredOptions1" :multiple="true"
                    :close-on-select="false" placeholder="Select Columns" @update:modelValue="onSelectionChange" />

                <label for="multiselect2" class="export-label">Select Columns for {{ this.mapping[1] }}:</label>
                <Multiselect id="multiselect2" v-model="selectedColumns2" :options="filteredOptions2" :multiple="true"
                    :close-on-select="false" placeholder="Select Columns" @update:modelValue="onSelectionChange" />
            </div>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import Multiselect from 'vue-multiselect';
import DOMPurify from 'dompurify';

export default {
    data() {
        return {
            selectedColumns1: [],
            selectedColumns2: [],
            allOptions: this.selectedColumns,
            mapping: this.graType,
        };
    },
    components: {
        Multiselect,
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
        filteredOptions1() {
            return this.allOptions.filter(option => !this.selectedColumns2.includes(option));
        },
        filteredOptions2() {
            return this.allOptions.filter(option => !this.selectedColumns1.includes(option));
        },
        ...mapState(['exportPath', 'exportFilename', 'exportFormat', "pageTitle", "graphType", "selectedColumns", "dateType"]),
    },
    methods: {
        ...mapActions(["updateExportPath", "updateExportFilename", "updateExportFormat", "updateGraphType", "updateMultiGraphType", "pushMessage"]),
        onSelectionChange() {
            const col1 = this.selectedColumns1.map(col => ({ name: col, type: this.mapping[0] }));
            const col2 = this.selectedColumns2.map(col => ({ name: col, type: this.mapping[1] }));
            const formats = [...col1, ...col2];

            // Check if all selected columns are in formats
            const allColumnsInFormats = this.allOptions.every(col => formats.some(format => format.name === col));
            if (!allColumnsInFormats) {
                this.pushMessage({ message: "All selected columns must be in the multi-graph formats", type: "error" });
            } else {
                this.pushMessage({ message: "All selected columns are in the multi-graph formats", type: "success" });
            }

            this.updateMultiGraphType(formats);
        },
    },
    watch: {
        graType() {
            this.mapping = this.graType.split('-');
        },
        selectedColumns() {
            this.allOptions = this.selectedColumns.filter(option => option !== this.dateType && !option.includes("ID"));
        },
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
