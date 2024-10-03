<template>
    <div class="statistics-container">
        <label for="statistics-select" class="statistics-label">Select Statistics:</label>
        <select id="statistics-select" v-model="selectedStatistics" multiple @change="onStatisticsChange"
            class="statistics-dropdown">
            <option value="None">None</option>
            <option value="Average">Average</option>
            <option value="Sum">Sum</option>
            <option value="Maximum">Maximum</option>
            <option value="Minimum">Minimum</option>
            <option value="Standard Deviation">Standard Deviation</option>
        </select>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    data() {
        return {
            selectedStatistics: ["None"],
        };
    },
    methods: {
        ...mapActions(["updateSelectedStatistics"]),
        onStatisticsChange() {
            this.updateSelectedStatistics(this.selectedStatistics);
        },
    },
};
</script>

<style scoped>
.statistics-container {
    display: flex;
    flex-direction: column;
    margin: 10px 0;
}

.statistics-label {
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 14px;
    color: #333;
}

.statistics-dropdown {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #fff;
    font-size: 14px;
    color: #333;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: border-color 0.2s ease-in-out;
    height: auto;
}

.statistics-dropdown:focus {
    border-color: #555;
    outline: none;
}

.statistics-dropdown:hover {
    border-color: #888;
}

.statistics-dropdown option {
    padding: 10px;
}

.statistics-dropdown[multiple] {
    height: auto;
    min-height: 150px;
    /* Adjusts height for better multiple selection view */
}

.statistics-dropdown option:hover {
    background-color: #f1f1f1;
}
</style>