<template>
    <div class="select-container">
        <div class="form-container">
            <div class="form-group">
                <label for="id-select">Select IDs:</label>
                <Multiselect v-model="selectIds" :options="ids" :multiple="true" :close-on-select="false"
                    :clear-on-select="false" :preserve-search="true" placeholder="Select IDs">
                </Multiselect>
            </div>
            <div class="form-group">
                <label for="date-start">Start Date:</label>
                <input type="date" v-if="['Time', 'Date'].includes(daType)" v-model="selectedDateStart"
                    class="input-field" />
                <input type="text" v-else-if="daType === 'Month'" v-model="selectedDateStart" placeholder="Enter month"
                    class="input-field" />
            </div>
            <div class="form-group">
                <label for="date-end">End Date:</label>
                <input type="date" v-if="['Time', 'Date'].includes(daType)" v-model="selectedDateEnd"
                    class="input-field" />
                <input type="text" v-else-if="daType === 'Month'" v-model="selectedDateEnd" placeholder="Enter month"
                    class="input-field" />
            </div>
        </div>
        <div class="form-container">
            <div class="form-group">
                <label for="id-select">Export Select IDs:</label>
                <Multiselect v-model="expIds" :options="ids" :multiple="true" :close-on-select="false"
                    :clear-on-select="false" :preserve-search="true" placeholder="Select IDs">
                </Multiselect>
            </div>

            <div class="form-group">
                <label for="date-start">Start Date:</label>
                <input type="date" v-if="['Time', 'Date'].includes(daType)" v-model="expDateStart"
                    class="input-field" />
                <input type="text" v-else-if="daType === 'Month'" v-model="expDateStart" placeholder="Enter month"
                    class="input-field" />
            </div>

            <div class="form-group">
                <label for="date-end">End Date:</label>
                <input type="date" v-if="['Time', 'Date'].includes(daType)" v-model="expDateEnd" class="input-field" />
                <input type="text" v-else-if="daType === 'Month'" v-model="expDateEnd" placeholder="Enter month"
                    class="input-field" />
            </div>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import Multiselect from 'vue-multiselect';
export default {
    components: { Multiselect },
    props: {
        selectedColumns: {
            type: Array,
            default: null
        }
    },
    computed: {
        // Binding selected IDs directly from Vuex
        selectIds: {
            get() {
                return this.selectedIds; // Get the value from Vuex
            },
            set(value) {
                this.updateSelectedIds(value); // Update Vuex state on change
                this.updateExportIds(value);
            }
        },
        // Binding date range (start and end) directly from Vuex
        selectedDateStart: {
            get() {
                return this.dateRange.start;
            },
            set(value) {
                this.updateSelectedDateStart(value);
                this.updateExportDateStart(value);
            }
        },
        selectedDateEnd: {
            get() {
                return this.dateRange.end; // Get the date range from Vuex
            },
            set(value) {
                this.updateSelectedDateEnd(value);
                this.updateExportDateEnd(value);
            }
        },
        daType() {
            return this.dateType; // Get the date type from Vuex (no need to set this directly)
        },
        expIds: {
            get() {
                return this.exportIds; // Get the value from Vuex
            },
            set(value) {
                this.updateExportIds(value);
            }
        },
        expDateStart: {
            get() {
                return this.exportDate.start; // Get the date range from Vuex
            },
            set(value) {
                this.updateExportDateStart(value);
            }
        },
        expDateEnd: {
            get() {
                return this.exportDate.end; // Get the date range from Vuex
            },
            set(value) {
                this.updateExportDateEnd(value);
            }
        },
        expDateType() {
            return this.exportDateType; // Get the date type from Vuex (no need to set this directly)
        },
        ...mapState(['columns', 'ids', 'selectedDb', 'selectedIds', 'dateRange', 'dateType', 'exportIds', 'exportDate', 'exportDateType']),
    },
    data() {
        return {
        };
    },
    methods: {
        ...mapActions(['fetchColumns', 'updateSelectedIds', 'updateSelectedDateStart', 'updateSelectedDateEnd', 'updateExportIds', 'updateExportDateStart', 'updateExportDateEnd']),
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style scoped>
.select-container {
    display: flex;
    flex-direction: row;
    gap: 5px;
    margin: 0px auto;
    min-width: 32%;
    justify-content: left;
    overflow-y: auto;
}


.form-container {
    display: flex;
    flex-direction: column;
    flex: 1; /* Allow containers to grow/shrink equally */
    width: 100%; /* Ensure a minimum width */
    gap: 5px;
    margin: 0px 0px;
    padding: 5px;
    background-color: #f9f9f9;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.form-group {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 8.35rem;
}

label {
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 14px;
}

.input-field {
    padding: 8px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 5px;
    width: 100%;
    margin-bottom: 2px;
}

input[type="date"],
input[type="text"] {
    height: 1.5rem;
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