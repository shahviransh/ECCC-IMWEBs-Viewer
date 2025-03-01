<template>
    <div class="folder-tree">
        <folder-tree :treeData="treeData" :page="pageTitle" @select="onSelect" />
    </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'; // Import Vuex helpers
import FolderTree from './FolderTree.vue';

export default {
    data() {
        return {
            selectedDb: null,
            selectedTable: null,
            selectedFolder: null,
            treeData: [],
            separator: '/',
        };
    },
    components: {
        FolderTree
    },
    computed: {
        ...mapState(['folderTree', 'tables', 'modelFolder', 'pageTitle']),
    },
    mounted() {
        this.fetchFolderTree();
    },
    watch: {
        folderTree() {
            if (this.treeData.length === 0 && Array.isArray(this.folderTree)) {
                this.treeData = this.listToTree(this.folderTree);
            }
        },
        tables() {
            if (this.selectedDb) {
                this.addTablesToTree();
            }
        },
        modelFolder() {
            if (this.modelFolder) {
                this.treeData = [];
                this.fetchFolderTree();
            }
        }
    },
    methods: {
        ...mapActions(['fetchFolderTree', 'fetchTables', 'removeSelectedGeoFolder', 'updateSelectedDbsTables', 'removeSelectedDbTable', 'updateSelectedGeoFolders']),
        listToTree(list) {
            let idCounter = 1;
            const tree = [];
            const lookup = {};

            list.forEach(item => {
                // Normalize paths to use the universal '/' separator
                const normalizedPath = item.name.replace(/\\/g, this.separator);
                const parts = normalizedPath.split(this.separator);

                let currentLevel = tree;

                parts.forEach((part, index) => {
                    const path = parts.slice(0, index + 1).join(this.separator);
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
                        selected: false,
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
            if (node) {
                if (node.type === 'database') {
                    this.selectedDb = node.path;
                    this.fetchTables(this.selectedDb);
                } else if (node.type === 'table') {
                    this.selectedTable = node.name;
                    this.updateSelectedDbsTables({
                        db: this.selectedDb,
                        table: this.selectedTable
                    });
                } else if (node.type === 'file') {
                    this.selectedFolder = node.path;
                    this.updateSelectedGeoFolders(this.selectedFolder);
                }
            } else {
                // Unselect table
                this.removeSelectedDbTable(this.selectedTable);
                this.removeSelectedGeoFolder(this.selectedFolder);
                this.selectedTable = null;
                this.selectedFolder = null;
            }
        }
    },
};
</script>

<style scoped>
.folder-tree {
    min-width: 200px;
}
</style>