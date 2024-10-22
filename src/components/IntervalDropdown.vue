<template>
    <div class="interval-export-container">
        <div class="interval-container">
            <label for="interval-select" class="interval-label">Select Interval:</label>
            <select id="interval-select" v-model="selectedInterval" @change="onIntervalChange"
                class="interval-dropdown">
                <option value="daily">Daily</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
                <option value="seasonally">Seasonally</option>
            </select>
        </div>

        <div class="interval-container">
            <label for="interval-select" class="interval-label">Export Select Interval:</label>
            <select id="interval-select" v-model="exportInterval" @change="onExportChange" class="interval-dropdown">
                <option value="daily">Daily</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
                <option value="seasonally">Seasonally</option>
            </select>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    data() {
        return {
            selectedInterval: "daily",
            exportInterval: "daily",
        };
    },
    methods: {
        ...mapActions(["updateSelectedInterval", "updateExportInterval"]),
        onIntervalChange() {
            this.exportInterval = this.selectedInterval;
            this.updateSelectedInterval(this.selectedInterval);
            this.updateExportInterval(this.selectedInterval);
        },
        onExportChange() {
            this.updateExportInterval(this.exportInterval);
        },
    },
};
</script>

<style scoped>
.interval-export-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin: 0px auto;
    justify-content: center;
}

.interval-container {
    display: flex;
    flex-direction: column;
    flex: 1; /* Allow containers to grow/shrink equally */
    min-width: 100px; /* Ensure a minimum width */
    gap: 5px;
    max-width: 200px;
    margin: 0px 0px;
    padding: 5px;
    background-color: #f9f9f9;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.interval-label {
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 14px;
}

.interval-dropdown {
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #fff;
    font-size: 14px;
    color: #333;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: border-color 0.2s ease-in-out;
}

.interval-dropdown:hover {
    border-color: #888;
}

.interval-dropdown:focus {
    border-color: #555;
    outline: none;
}
</style>