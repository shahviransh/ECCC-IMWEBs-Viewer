<template>
    <div class="statistics-container">
        <label for="statistics-select" class="statistics-label">Select Statistics:</label>
        <Multiselect v-model="selectedStatistics" :options="option" :multiple="true" :close-on-select="false"
            :clear-on-select="false" :preserve-search="true" @update:modelValue="onStatisticsChange">
        </Multiselect>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import Multiselect from 'vue-multiselect';

export default {
    data() {
        return {
            selectedStatistics: ["None"],
            option: ["None", "Average", "Sum", "Maximum", "Minimum", "Standard Deviation"],
        };
    },
    components: {
        Multiselect,
    },
    methods: {
        ...mapActions(["updateSelectedStatistics"]),
        onStatisticsChange() {
            this.updateSelectedStatistics(this.selectedStatistics);
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style>
.multiselect {
    font-size: 14px;
}

.multiselect__tag {
    padding: 2px 18px 2px 5px;
    margin-right: 5px;
    font-size: 14px;
}

.multiselect__tag-icon {
    line-height: 18px;
}
</style>
<style scoped>
.statistics-container {
    display: flex;
    flex-direction: column;
    margin: 5px 0;
}

.statistics-label {
    font-weight: 600;
    margin-bottom: 0px;
    font-size: 14px;
    color: #333;
}
</style>