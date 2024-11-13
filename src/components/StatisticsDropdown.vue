<template>
    <div class="statistics-container">
        <label for="statistics-select" class="statistics-label">Select Statistics:</label>
        <Multiselect id="statistics-select" v-model="selectedStatistics" :options="option" :multiple="true" :close-on-select="false"
            :clear-on-select="false" :preserve-search="true" @update:modelValue="onStatisticsChange" :class="tagClass">
        </Multiselect>
        <label for="method-select" class="method-label">Select Method:</label>
        <Multiselect id="method-select" v-model="selectedMethod" :options="option" :multiple="true" :close-on-select="false"
            :clear-on-select="false" :preserve-search="true"
            @update:modelValue="onMethodChange" :class="tagClassMethod">
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
            selectedMethod: ["Equal"],
            options: ["Equal", "Average", "Sum", "Maximum", "Minimum"],
        };
    },
    computed: {
        tagClass() {
            return this.selectedStatistics.length > 4 ? 'small-tags' : 'normal-tags';
        },
        tagClassMethod() {
            return this.selectedMethod.length > 4 ? 'small-tags' : 'normal-tags';
        }
    },
    components: {
        Multiselect,
    },
    methods: {
        ...mapActions(["updateSelectedStatistics", "updateSelectedMethod"]),
        onStatisticsChange() {
            this.updateSelectedStatistics(this.selectedStatistics);
        },
        onMethodChange() {
            this.updateSelectedMethod(this.selectedMethod);
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
    font-size: 12px;
}

.multiselect__tag-icon {
    line-height: 16px;
}

.small-tags .multiselect__tag {
    font-size: 8px;
}

.normal-tags .multiselect__tag {
    font-size: 12px;
}
</style>
<style scoped>
.statistics-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin: 0px 0px;
    padding: 5px;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    background-color: antiquewhite;
}

.statistics-label {
    font-weight: 600;
    margin-bottom: 0px;
    font-size: 14px;
    color: #333;
}

.method-label {
    font-weight: 600;
    font-size: 14px;
    color: #333;
    margin-bottom: 0px;
}
</style>