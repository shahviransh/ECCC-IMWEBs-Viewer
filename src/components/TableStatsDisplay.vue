<template>
    <div class="main-view">
        <!-- Table Container with Scrollable Body -->
        <div class="table-container">
            <table class="styled-table">
                <thead>
                    <tr>
                        <th v-for="column in selectedColumns" :key="column">{{ column }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, index) in visibleData" :key="index">
                        <td v-for="column in selectedColumns" :key="column">{{ row[column] }}</td>
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
        id: [String, null],
        ID: String,
        rowLimit: [Number],
    },
    data() {
        return {
            visibleData: [],
            canLoadMore: true,
        };
    },
    computed: {
        filteredData() {
            if (!this.id) {
                return this.data;
            }
            return this.data.filter(row => row[this.ID] === this.id);
        },
    },
    methods: {
        // Load initial rows when the data is loaded
        loadInitialRows() {
            this.visibleData = this.data.slice(0, this.rowLimit);
            this.canLoadMore = this.data.length > this.rowLimit;
        },
        // Load more rows when the load more button is clicked
        loadMoreRows() {
            const nextRowLimit = this.visibleData.length + this.rowLimit;
            const nextRows = this.data.slice(this.visibleData.length, nextRowLimit);
            // Append the next rows to the visible data
            this.visibleData = [...this.visibleData, ...nextRows];
            // Check if we can load more rows
            if (this.visibleData.length >= this.data.length) {
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