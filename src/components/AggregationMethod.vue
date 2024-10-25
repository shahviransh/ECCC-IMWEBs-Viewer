<template>
    <div class="method-container">
        <label for="method-select" class="method-label">Select Method:</label>
        <Multiselect v-model="selectedMethod" :options="option" :multiple="true" :close-on-select="false"
            :clear-on-select="false" :preserve-search="true"
            @update:modelValue="onMethodChange" :class="tagClass">
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
    computed: {
        tagClass() {
            return this.selectedMethod.length > 4 ? 'small-tags' : 'normal-tags';
        }
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style>
.small-tags .multiselect__tag {
    font-size: 10px;
}

.normal-tags .multiselect__tag {
    font-size: 12px;
}
</style>
<style scoped>
/* Reduce width of the dropdown */
.multiselect {
    /* Set the desired width */
    font-size: 14px;
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