<template>
    <h5 class="parameter-heading">Parameters:</h5>
    <div v-if="pageTitle === 'Project'">
        <div class="form-container">
            <div class="form-group">
                <label for="column-select">Select Columns:</label>
                <select id="column-select" class="dropdown" v-model="selectColumns" multiple
                    :style="{ height: heightVar() }">
                    <option v-for="column in columns" :key="column" :value="column">{{ column }}</option>
                </select>
            </div>
        </div>
        <div class="form-container">
            <div class="form-group">
                <label for="export-column-select">Export Select Columns:</label>
                <select id="export-column-select" class="dropdown" v-model="expColumns" multiple
                    :style="{ height: heightVar() }">
                    <option v-for="column in columns" :key="column" :value="column">{{ column }}</option>
                </select>
            </div>
        </div>
    </div>
    <!-- Conditional Axes Dropdowns -->
    <div v-if="pageTitle === 'Graph'">
        <div class="form-container x-axis">
            <div class="form-group">
                <label for="x-axis-select">X-Axis:</label>
                <select id="x-axis-select" class="dropdown" v-model="xaxis" :style="{ height: heightVar() }">
                    <option v-for="column in columns.filter(col => col === dateType)" :key="column"
                        :value="column">{{ column }}</option>
                </select>
            </div>
        </div>
        <div class="form-container">
            <div class="form-group">
                <label for="y-axis-select">Y-Axis:</label>
                <select id="y-axis-select" class="dropdown" v-model="yaxis" multiple :style="{ height: heightVar() }">
                    <option v-for="column in columns.filter(col => col !== dateType)" :key="column"
                        :value="column">{{ column }}</option>
                </select>
            </div>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    props: {
        selectedTable: {
            type: String,
            default: null
        }
    },
    computed: {
        // Binding selected columns directly from Vuex
        selectColumns: {
            get() {
                return this.selectedColumns; // Get the value from Vuex
            },
            set(value) {
                this.updateSelectedColumns(value); // Update Vuex state on change
                this.updateExportColumns(this.selectedColumns); // Update export columns based on selected columns
            }
        },
        expColumns: {
            get() {
                return this.exportColumns;
            },
            set(value) {
                this.updateExportColumns(value);
            }
        },
        xaxis: {
            get() {
                return this.xAxis;
            },
            set(value) {
                this.updateXAxis(value);
            }
        },
        yaxis: {
            get() {
                return this.yAxis
            },
            set(value) {
                this.updateYAxis(value);
            }
        },
        ...mapState(['columns', 'ids', 'selectedDb', 'selectedColumns', 'exportColumns', 'pageTitle', 'xAxis', 'yAxis', 'dateType'])
    },
    data() {
        return {
        };
    },
    watch: {
        selectedTable(newTable) {
            this.fetchColumns({ db: this.selectedDb, table: newTable });
        },
    },
    methods: {
        ...mapActions(['fetchColumns', 'updateSelectedColumns', 'updateExportColumns', 'updateXAxis', 'updateYAxis']),
        heightVar() {
            const isTauri = window.isTauri !== undefined;
            return isTauri ? '36vh' : '34vh';
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style scoped>
.parameter-heading {
    font-size: 16px;
    font-weight: 600;
    margin: 0px 0px 0px 0px;
    color: #333;
}

.form-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    max-width: 500px;
    margin: 0px auto;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    height: 45%;
    /* Set the total height of the container */
}

.form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;
}

label {
    font-weight: 600;
    margin: 0px 0px 0px 0px;
    font-size: 14px;
}

.dropdown {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #fff;
    font-size: 14px;
    width: 100%;
}

.dropdown[multiple] {
    padding: 5px;
    overflow-y: auto;
}
</style>