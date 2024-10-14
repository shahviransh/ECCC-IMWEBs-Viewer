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
    gap: 5px;
    max-width: 500px;
    margin: 0px auto;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    height: 46.5%; /* Set the total height of the container */
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
    height: 40px;
}

.dropdown[multiple] {
    height: 16rem;
    padding: 5px;
    overflow-y: auto; /* Allows scrolling */
}
</style>