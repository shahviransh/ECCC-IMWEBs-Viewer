<template>
    <div class="dropdown-container">
        <label for="db-select">Select Database:</label>
        <select id="db-select" v-model="selectedDb" @change="onDatabaseChange" class="dropdown-select">
            <option v-for="db in databases" :key="db.name" :value="db.name">{{ db.name }}</option>
        </select>
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers

export default {
    data() {
        return {
            selectedDb: null,
            treeData: [],
        };
    },
    computed: {
        ...mapState(['databases']),
    },
    mounted() {
        this.fetchDatabases();
    },
    watch: {
        databases: function () {
            if (this.treeData.length === 0) {
                this.treeData = [...this.listToTree(this.databases)];
            }
        }
    },
    methods: {
        ...mapActions(['fetchDatabases', 'updateSelectedDb']),
        onDatabaseChange() {
            this.updateSelectedDb(this.selectedDb);
        },
        listToTree(list) {
            let idCounter = 1; // Initialize ID counter

            const tree = [];
            const lookup = {};

            list.forEach(item => {
                const parts = item.name.split('\\');
                let currentLevel = tree;

                parts.forEach((part, index) => {
                    let existingNode = currentLevel.find(node => node.label === part);

                    if (!existingNode) {
                        // Create new node with an id
                        existingNode = {
                            id: idCounter++, // Assign an id and increment the counter
                            name: part,
                            type: index === parts.length - 1 ? item.type : 'folder',
                            children: []
                        };
                        currentLevel.push(existingNode);
                    }

                    // Move to the next level (children)
                    currentLevel = existingNode.children;
                });
            });

            return tree;
        },
        onSelect(node) {
            if (node.type === 'file') {
                alert(`You selected file: ${node.label}`);
            }
        }
    },
};
</script>

<style scoped>
.dropdown-container {
    display: flex;
    flex-direction: column;
    margin: 10px;
}

.dropdown-select {
    width: 100%;
    /* Adjust this to fit the container */
    max-width: 300px;
    /* Maximum width */
    min-width: 200px;
    /* Minimum width */
    padding: 8px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    /* Ensure padding does not affect width */
}

.dropdown-select option {
    padding: 8px;
}
</style>