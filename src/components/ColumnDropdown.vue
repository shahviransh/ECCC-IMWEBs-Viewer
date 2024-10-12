<template>
    <div class="form-container">
        <div class="form-group">
            <label for="column-select">Select Columns:</label>
            <select class="dropdown" v-model="selectColumns" multiple>
                <option v-for="column in columns" :key="column" :value="column">{{ column }}</option>
            </select>
        </div>
    </div>
    <div class="form-container">
        <div class="form-group">
            <label for="column-select">Export Select Columns:</label>
            <select class="dropdown" v-model="expColumns" multiple>
                <option v-for="column in columns" :key="column" :value="column">{{ column }}</option>
            </select>
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
        ...mapState(['columns', 'ids', 'selectedDb', 'selectedColumns', 'exportColumns']),
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
        ...mapActions(['fetchColumns', 'updateSelectedColumns', 'updateExportColumns']),
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style scoped>
.form-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 500px;
    margin: 20px auto;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    height: 38%; /* Set the total height of the container */
}

.form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;
}

label {
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 14px;
}

.dropdown {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #fff;
    font-size: 14px;
    width: 100%;
    height: 40px;
}

input.input-field {
    padding: 10px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 5px;
    width: 100%;
}

.dropdown[multiple] {
    height: auto;
    padding: 5px;
    min-height: 200px; /* You can adjust the minimum height */
    overflow-y: auto; /* Allows scrolling */
}

input[type="date"],
input[type="text"] {
    height: 25px;
    box-sizing: border-box;
}

input[type="date"]::-webkit-calendar-picker-indicator {
    cursor: pointer;
}

input[type="text"]::placeholder {
    color: #999;
    font-style: italic;
}
</style>