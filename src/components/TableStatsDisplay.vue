<template>
    <div class="main-view">
        <!-- Table Container with Scrollable Body -->
        <div class="table-container">
            <table class="styled-table">
                <thead>
                    <tr>
                        <th v-for="column in selectedColumns.filter(c => !properties.includes(c))" :key="column">{{
                            column }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, index) in visibleData" :key="index">
                        <td v-for="column in selectedColumns.filter(c => !properties.includes(c))" :key="column">{{
                            row[column] }}</td>
                    </tr>
                </tbody>
            </table>
            <!-- Load More Button -->
            <div v-if="canLoadMore" class="load-more-container">
                <button class="load-more-button" @click="loadMoreRows">Load More</button>
            </div>
        </div>
        <h2 v-if="stats.length > 0">Stats for all selected IDs:</h2>
        <!-- Stats Container with Scrollable Body -->
        <div class="stats-container">
            <table class="styled-table">
                <thead>
                    <tr>
                        <th v-for="column in statsColumns" :key="column">{{ column }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, index) in stats" :key="index">
                        <td v-for="column in statsColumns" :key="column">{{ row[column] }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        data: Array,
        stats: Array,
        selectedColumns: Array,
        statsColumns: Array,
        properties: Array,
        id: [Number, null],
        ID: String,
        rowLimit: [Number],
    },
    data() {
        return {
            visibleData: [],
            canLoadMore: true,
            filteredData: [],
        };
    },
    mounted() {
        this.filteredData = this.id ? this.data.filter(row => row[this.ID] === this.id) : this.data;
    },
    methods: {
        // Load initial rows when the data is loaded
        loadInitialRows() {
            this.visibleData = this.filteredData.slice(0, this.rowLimit);
            this.canLoadMore = this.filteredData.length > this.rowLimit;
        },
        // Load more rows when the load more button is clicked
        loadMoreRows() {
            const nextRowLimit = this.visibleData.length + this.rowLimit;
            const nextRows = this.filteredData.slice(this.visibleData.length, nextRowLimit);
            // Append the next rows to the visible data
            this.visibleData = [...this.visibleData, ...nextRows];
            // Check if we can load more rows
            if (this.visibleData.length >= this.filteredData.length) {
                this.canLoadMore = false;
            }
        },
    },
    watch: {
        data: {
            immediate: true,
            handler() {
                this.loadInitialRows();
            }
        }
    }
};
</script>
<style src="../assets/pages.css" />