<template>
    <div class="dropdown-container">
        <label for="db-select">Select Database:</label>
        <select id="db-select" v-model="selectedDb" @change="onDatabaseChange" class="dropdown-select">
            <option v-for="db in databases" :key="db.name" :value="db.name">{{ db.name }}</option>
        </select>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            databases: [],
            selectedDb: null,
        };
    },
    mounted() {
        this.fetchDatabases();
    },
    methods: {
        async fetchDatabases() {
            const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL;  // Dynamic base URL from .env
            try {
                const response = await axios.get(`${apiBaseUrl}/api/list_files`, {
                    params: { folder_path: 'Jenette_Creek_Watershed' }
                });
                this.databases = response.data;
            } catch (error) {
                this.error = "Error retrieving files: " + error;
                console.error(this.error);
            }
        },
        onDatabaseChange() {
            this.$emit("database-selected", this.selectedDb);
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