<template>
    <div class="interval-container">
        <label for="interval-select" class="interval-label">Select Interval:</label>
        <select id="interval-select" v-model="selectInterval" class="interval-dropdown">
            <option value="daily">Daily</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
            <option value="seasonally">Seasonally</option>
        </select>

        <label for="export-interval-select" class="interval-label">Export Select Interval:</label>
        <select id="export-interval-select" v-model="expInterval" @change="onExportChange" class="interval-dropdown">
            <option value="daily">Daily</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
            <option value="seasonally">Seasonally</option>
        </select>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    data() {
        return {
        };
    },
    computed: {
        selectInterval: {
            get() {
                return this.selectedInterval;
            },
            set(value) {
                this.updateSelectedInterval(value);
                this.updateExportInterval(value); // Update export interval as well to match selected interval
            }
        },
        expInterval: {
            get() {
                return this.exportInterval;
            },
            set(value) {
                this.updateExportInterval(value);
            }
        },
        ...mapState(["selectedInterval", "exportInterval"]),
    },
    methods: {
        ...mapActions(["updateSelectedInterval", "updateExportInterval"]),
        onExportChange() {
            if (this.isValidExportInterval(this.selectedInterval, this.exportInterval)) {
                this.updateExportInterval(this.exportInterval);
            } else {
                alert("Export interval cannot be less than the selected interval.");
                this.updateExportInterval(this.selectedInterval);
            }
        },
        isValidExportInterval(importInterval, exportInterval) {
            const intervals = ["daily", "monthly", "seasonally", "yearly"];
            return intervals.indexOf(exportInterval) >= intervals.indexOf(importInterval);
        }
    },
};
</script>

<style scoped>
.interval-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    max-width: 200px;
    margin: 0px 0px;
    padding: 5px;
    background-color: antiquewhite;
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