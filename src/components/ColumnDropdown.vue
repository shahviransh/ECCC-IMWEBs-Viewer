<template>
    <div class="form-container">
        <div class="form-group">
            <label for="column-select">Select Columns:</label>
            <select id="column-select" v-model="selectedColumns" multiple @change="onChange" class="dropdown">
                <option v-for="column in columns" :key="column" :value="column">{{
                    column }}</option>
            </select>
        </div>

        <div class="form-group">
            <label for="id-select">Select IDs:</label>
            <select id="id-select" v-model="selectedIds" multiple @change="onChange" class="dropdown">
                <option v-for="id in ids" :key="id" :value="id">{{ id }}</option>
            </select>
        </div>

        <div class="form-group">
            <label for="date-start">Start Date:</label>
            <input type="date" v-if="dateType === 'Time'" v-model="selectedDate.start" @change="onChange"
                class="input-field" />
            <input type="text" v-else-if="dateType === 'Month'" v-model="selectedDate.start" @change="onChange"
                placeholder="Enter month" class="input-field" />
        </div>

        <div class="form-group">
            <label for="date-end">End Date:</label>
            <input type="date" v-if="dateType === 'Time'" v-model="selectedDate.end" @change="onChange"
                class="input-field" />
            <input type="text" v-else-if="dateType === 'Month'" v-model="selectedDate.end" @change="onChange"
                placeholder="Enter month" class="input-field" />
        </div>
    </div>
    <div class="form-container">
        <div class="form-group">
            <label for="column-select">Export Select Columns:</label>
            <select id="column-select" v-model="exportColumns" multiple @change="onChangeExport" class="dropdown">
                <option v-for="column in columns" :key="column" :value="column">{{
                    column }}</option>
            </select>
        </div>

        <div class="form-group">
            <label for="id-select">Select IDs:</label>
            <select id="id-select" v-model="exportIds" multiple @change="onChangeExport" class="dropdown">
                <option v-for="id in ids" :key="id" :value="id">{{ id }}</option>
            </select>
        </div>

        <div class="form-group">
            <label for="date-start">Start Date:</label>
            <input type="date" v-if="dateType === 'Time'" v-model="exportDate.start" @change="onChangeExport"
                class="input-field" />
            <input type="text" v-else-if="dateType === 'Month'" v-model="exportDate.start" @change="onChangeExport"
                placeholder="Enter month" class="input-field" />
        </div>

        <div class="form-group">
            <label for="date-end">End Date:</label>
            <input type="date" v-if="dateType === 'Time'" v-model="exportDate.end" @change="onChangeExport"
                class="input-field" />
            <input type="text" v-else-if="dateType === 'Month'" v-model="exportDate.end" @change="onChangeExport"
                placeholder="Enter month" class="input-field" />
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {
    props: {
        selectedDb: {
            type: String,
            default: null,
        },
        selectedTable: {
            type: String,
            default: null,
        },
    },
    data() {
        return {
            columns: [],
            selectedColumns: [],
            exportColumns: [],
            ids: [],
            selectedIds: [],
            exportIds: [],
            selectedDate: {
                start: null,
                end: null,
            },
            exportDate: {
                start: null,
                end: null,
            },
            dateType: null,
            exportDateType: null,
        };
    },
    watch: {
        selectedTable(newTable) {
            this.fetchColumns(newTable);
        },
    },
    methods: {
        async fetchColumns(newTable) {
            const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL;
            try {
                const response = await axios.get(`${apiBaseUrl}/api/get_table_details`, {
                    params: {
                        db_path: this.selectedDb,
                        table_name: newTable,
                    },
                });
                this.columns = response.data.columns;
                this.ids = response.data.ids;
                this.selectedDate = {
                    start: response.data.start_date,
                    end: response.data.end_date,
                };
                this.dateType = response.data.date_type;
                this.exportDate = {
                    start: response.data.start_date,
                    end: response.data.end_date,
                };
                this.exportDateType = response.data.date_type;
            } catch (error) {
                console.error("Error fetching columns:", error);
            }
        },
        onChange() {
            this.exportColumns = [...this.selectedColumns];
            this.exportIds = [...this.selectedIds];
            this.exportDate = { ...this.selectedDate };
            this.exportDateType = this.dateType;

            this.$emit("columns-selected", {
                selectedColumns: this.selectedColumns,
                selectedIds: this.selectedIds,
                selectedDate: this.selectedDate,
                dateType: this.dateType,
            });
        },
        onChangeExport() {
            this.$emit("export-selected", {
                selectedColumns: this.exportColumns,
                selectedIds: this.exportIds,
                selectedDate: this.exportDate,
                dateType: this.exportDateType,
            });
        },
    },
};
</script>

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
}

.form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;
}

label {
    font-weight: 600;
    margin-bottom: 5px;
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
}

input[type="date"],
input[type="text"] {
    height: 40px;
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