<template>
    <div class="method-container">
        <label for="method-select" class="method-label">Select Method:</label>
        <select id="method-select" v-model="selectedMethod" multiple @change="onMethodChange" class="method-dropdown">
            <option value="Equal">Equal</option>
            <option value="Average">Average</option>
            <option value="Sum">Sum</option>
            <option value="Maximum">Maximum</option>
            <option value="Minimum">Minimum</option>
        </select>
    </div>
</template>

<script>
export default {
    data() {
        return {
            selectedMethod: ["Equal"],
        };
    },
    methods: {
        onMethodChange() {
            this.$emit("method-selected", this.selectedMethod);
        },
    },
};
</script>

<style scoped>
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