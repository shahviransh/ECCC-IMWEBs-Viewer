<template>
    <div class="dropdown-container">
        <label for="db-select">Select Database:</label>
        <select id="db-select" v-model="selectedDb" @change="onDatabaseChange" class="dropdown-select">
            <option v-for="db in databases" :key="db.name" :value="db.name">{{ db.name }}</option>
        </select>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    data() {
        return {
            selectedDb: null,
        };
    },
    computed: {
        ...mapState(['databases']),
    },
    mounted() {
        this.fetchDatabases();
    },
    methods: {
        ...mapActions(['fetchDatabases', 'updateSelectedDb']),
        onDatabaseChange() {
            this.updateSelectedDb(this.selectedDb);
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