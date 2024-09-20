<template>
    <div class="dropdown-container">
        <label for="table-select">Select Table:</label>
        <select id="table-select" v-model="selectedTable" @change="onTableChange" class="dropdown-select">
            <option v-for="table in tables" :key="table" :value="table">{{ table }}</option>
        </select>
    </div>
</template>

<script>
import axios from "axios";

export default {
    props: {
        selectedDb: {
            type: String,
            default: null
        }
    },
    data() {
        return {
            tables: [],
            selectedTable: null,
        };
    },
    watch: {
        // Watch for changes in the selectedDb prop
        selectedDb(newDb) {
            this.fetchTables(newDb);
        },
    },
    methods: {
        async fetchTables(newDb) {
            const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL;
            try {
                const response = await axios.get(`${apiBaseUrl}/api/get_tables`, {
                    params: { db_path: newDb }
                });
                this.tables = response.data;
            } catch (error) {
                console.error('Error fetching tables:', error);
            }
        },
        onTableChange() {
            this.$emit("table-selected", this.selectedTable);
        },
    },
};
</script>

<style scoped>
.dropdown-container {
    display: flex;
    flex-direction: column;
    margin: 10px;
}

.dropdown-select {
    width: 100%;
    /* Adjust this to fit the container */
    max-width: 300px;
    /* Maximum width */
    min-width: 200px;
    /* Minimum width */
    padding: 8px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    /* Ensure padding does not affect width */
}

.dropdown-select option {
    padding: 8px;
}
</style>