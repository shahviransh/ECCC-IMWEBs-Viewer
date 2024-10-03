<template>
    <div class="dropdown-container">
        <label for="table-select">Select Table:</label>
        <select id="table-select" v-model="selectedTable" @change="onTableChange" class="dropdown-select">
            <option v-for="table in tables" :key="table" :value="table">{{ table }}</option>
        </select>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    props: {
        selectedDb: {
            type: String,
            default: null
        }
    },
    data() {
        return {
            selectedTable: null,
        };
    },
    computed: {
        ...mapState(['tables']),
    },
    watch: {
        selectedDb(newDb) {
            this.fetchTables(newDb);
        }
    },
    methods: {
        ...mapActions(['fetchTables', 'updateSelectedTable']),
        onTableChange() {
            this.updateSelectedTable(this.selectedTable);
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