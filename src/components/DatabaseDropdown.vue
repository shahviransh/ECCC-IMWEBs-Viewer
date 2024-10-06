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
        ...mapState(['databases', 'tables']),
    },
    mounted() {
        this.fetchDatabases();
    },
    watch: {
        databases() {
            if (this.treeData.length === 0) {
                this.treeData = this.listToTree(this.databases);
            }
        },
        tables() {
            if (this.selectedDb) {
                this.addTablesToTree();
            }
        }
    },
    methods: {
        ...mapActions(['fetchDatabases', 'updateSelectedDb', 'fetchTables']),
        onDatabaseChange() {
            this.updateSelectedDb(this.selectedDb);
            this.fetchTables(this.selectedDb);
        },
        listToTree(list) {
            let idCounter = 1;
            const tree = [];
            const lookup = {};

            list.forEach(item => {
                const parts = item.name.split('\\');
                let currentLevel = tree;

                parts.forEach((part, index) => {
                    const path = parts.slice(0, index + 1).join('\\');
                    let existingNode = lookup[path]; // Check if the path already exists

                    if (!existingNode) {
                        // Create new node with an id
                        existingNode = {
                            id: idCounter++,
                            name: part,
                            type: index === parts.length - 1 ? item.type : 'folder',
                            children: []
                        };
                        currentLevel.push(existingNode);
                    }

                    // Move to the next level (children)
                    currentLevel = existingNode.children;
                    lookup[path] = existingNode;
                });
            });

            return tree;
        },
        addTablesToTree() {
            // Traverse the tree and find the selected database node
            const selectedDbNode = this.findNode(this.treeData[0], this.selectedDb);

            if (selectedDbNode && this.tables) {
                // Clear existing tables from the selectedDbNode's children if they already exist
                selectedDbNode.children = selectedDbNode.children.filter(child => child.type !== 'table');
                // Add tables as children of the selected database node
                this.tables.forEach(table => {
                    selectedDbNode.children.push({
                        id: `table-${table}`,
                        name: table,
                        type: 'table',
                        children: [] // Tables don't have further children
                    });
                });
            }
        },
        findNode(node, id) {
            if (id.includes(node.name) && node.type === 'file') {
                return node;
            } else if (node.children) {
                let result = null;
                for (let i = 0; result === null && i < node.children.length; i++) {
                    result = this.findNode(node.children[i], id);
                }
                return result;
            }
            return null;
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