<template>
    <div :class="[theme, 'interval-container']">
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
        <template v-if="[selectInterval, expInterval].includes('monthly') && pageTiltle === 'Map'">
            <label for="month-interval-select" class="interval-label">Select Month:</label>
            <select id="month-interval-select" v-model="monInterval" class="interval-dropdown">
                <option value="1">January</option>
                <option value="2">February</option>
                <option value="3">March</option>
                <option value="4">April</option>
                <option value="5">May</option>
                <option value="6">June</option>
                <option value="7">July</option>
                <option value="8">August</option>
                <option value="9">September</option>
                <option value="10">October</option>
                <option value="11">November</option>
                <option value="12">December</option>
            </select>
        </template>
        <template v-if="[selectInterval, expInterval].includes('seasonally') && pageTiltle === 'Map'">
            <label for="season-interval-select" class="interval-label">Select Season:</label>
            <select id="season-interval-select" v-model="seaInterval" class="interval-dropdown">
                <option value="summer">Summer</option>
                <option value="fall">Fall</option>
                <option value="winter">Winter</option>
                <option value="spring">Spring</option>
            </select>
        </template>
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
        monInterval: {
            get() {
                return this.selectedMonth;
            },
            set(value) {
                this.updateSelectedMonth(value);
            }
        },
        seaInterval: {
            get() {
                return this.selectedSeason;
            },
            set(value) {
                this.updateSelectedSeason(value);
            }
        },
        ...mapState(["selectedInterval", "exportInterval", "selectedSeason", "selectedMonth", "theme", "pageTitle"]),
    },
    methods: {
        ...mapActions(["updateSelectedInterval", "updateExportInterval", "updateSelectedMonth", "updateSelectedSeason"]),
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
/* Theme variables */
.light {
    --text-color: #333;
    --bg-color: antiquewhite;
    --border-color: #ccc;
    --box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    --focus-border: #555;
}

.dark {
    --text-color: #f9f9f9;
    --bg-color: #444;
    --border-color: #666;
    --box-shadow: 0 2px 5px rgba(255, 255, 255, 0.1);
    --focus-border: #888;
}

.interval-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    max-width: 200px;
    margin: 0px 0px;
    padding: 5px;
    background-color: var(--bg-color);
    border-radius: 4px;
    box-shadow: var(--box-shadow);
}

.interval-label {
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 14px;
    color: var(--text-color);
}

.interval-dropdown {
    padding: 5px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background-color: var(--bg-color);
    font-size: 14px;
    color: var(--text-color);
    cursor: pointer;
    box-shadow: var(--box-shadow);
    transition: border-color 0.2s ease-in-out;
}

.interval-dropdown:hover {
    border-color: var(--focus-border);
}

.interval-dropdown:focus {
    border-color: var(--focus-border);
    outline: none;
}
</style>