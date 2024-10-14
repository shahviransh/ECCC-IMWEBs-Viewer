<template>
    <folder-tree :treeData="treeData" @select="onSelect" />
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import FolderTree from './FolderTree.vue';

export default {
    data() {
        return {
            selectedDb: null,
            selectedTable: null,
            treeData: [],
        };
    },
    components: {
        FolderTree
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
        ...mapActions(['fetchDatabases', 'updateSelectedDb', 'fetchTables', 'updateSelectedTable']),
        listToTree(list) {
            let idCounter = 1;
            const tree = [];
            const lookup = {};

            const isWindows = navigator.platform.indexOf('Win') > -1;
            const separator = isWindows ? '\\' : '/';

            list.forEach(item => {
                const parts = item.name.split(separator);
                let currentLevel = tree;

                parts.forEach((part, index) => {
                    const path = parts.slice(0, index + 1).join(separator);
                    let existingNode = lookup[path]; // Check if the path already exists

                    if (!existingNode) {
                        // Create new node with an id
                        existingNode = {
                            id: idCounter++,
                            name: part,
                            type: index === parts.length - 1 ? item.type : 'folder',
                            path: path,
                            expanded: false,
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
                        expanded: false,
                        children: [] // Tables don't have further children
                    });
                });
            }
        },
        findNode(node, id) {
            if (id.includes(node.name) && node.type === 'database') {
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
            if (node.type === 'database') {
                // Handle folder selection
                this.selectedDb = node.path;
                this.updateSelectedDb(this.selectedDb);
                this.fetchTables(this.selectedDb);
            } else if (node.type === 'table') {
                // Handle table selection
                this.selectedTable = node.name;
                this.updateSelectedTable(this.selectedTable);
            }
        }
    },
};
</script>
