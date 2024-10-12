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

/* Reduce width of the dropdown */
.multiselect {
    /* Set the desired width */
    font-size: 14px;
    overflow-y: auto;
    max-height: 65px;
}

.method-container {
    display: flex;
    flex-direction: column;
    margin: 5px 0;
}

.method-label {
    font-weight: 600;
    font-size: 14px;
    color: #333;
    margin-bottom: 0px;
}
</style>