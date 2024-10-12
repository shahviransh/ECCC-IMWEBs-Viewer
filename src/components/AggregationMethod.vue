<template>
    <div class="method-container">
        <label for="method-select" class="method-label">Select Method:</label>
        <Multiselect v-model="selectedMethod" :options="option" :multiple="true" :close-on-select="false"
            :clear-on-select="false" :preserve-search="true"
            @update:modelValue="onMethodChange">
        </Multiselect>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import Multiselect from 'vue-multiselect';
export default {
    data() {
        return {
            selectedMethod: ["Equal"],
            option: ["Equal", "Average", "Sum", "Maximum", "Minimum"],
        };
    },
    components: {
        Multiselect,
    },
    methods: {
        ...mapActions(["updateSelectedMethod"]),
        onMethodChange() {
            this.updateSelectedMethod(this.selectedMethod);
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style scoped>
.multiselect__content-wrapper {
    z-index: 1000; /* or a higher value */
}

.method-container {
    display: flex;
    flex-direction: column;
    margin: 10px 0;
}

.method-label {
    font-weight: 600;
    font-size: 14px;
    color: #333;
    margin-bottom: 5px;
}

.method-dropdown {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #fff;
    font-size: 14px;
    color: #333;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: border-color 0.3s ease-in-out;
    height: auto;
}

.method-dropdown:focus {
    border-color: #555;
    outline: none;
}

.method-dropdown:hover {
    border-color: #888;
}

.method-dropdown option {
    padding: 10px;
}

.method-dropdown[multiple] {
    height: auto;
    min-height: 120px;
    /* Adjust height for better multiple selection view */
    max-height: 180px;
    /* Limit height */
    overflow-y: auto;
    /* Add scroll for overflow */
}

.method-dropdown option:hover {
    background-color: #f1f1f1;
}
</style>