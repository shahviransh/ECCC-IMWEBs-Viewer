<template>
    <div class="folder-tree">
        <ul>
            <li v-for="node in treeData" :key="node.id">
                <div :class="['node', { 'folder-node': node.type === 'folder', 'file-node': node.type === 'file' }]"
                    @click="toggleNode(node)">
                    <span v-if="node.type === 'folder'">{{ node.expanded ? '📂' : '📁' }}</span>
                    <span v-else>📄</span>
                    {{ node.name }}
                </div>
                <!-- Recursively display children if the node is expanded -->
                <folder-tree v-if="node.children && node.children.length > 0 && node.expanded" :treeData="node.children"
                    @select="onSelect" />
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    name: 'FolderTree',
    props: {
        treeData: {
            type: Array,
            required: true
        }
    },
    methods: {
        toggleNode(node) {
            if (node.type === 'folder' || node.type === 'file') {
                // Toggle the expanded state directly
                node.expanded = !node.expanded;
            }
            // Emit the selected node to the parent
            this.$emit('select', node);
        },
        onSelect(node) {
            // Propagate the select event upwards
            this.$emit('select', node);
        }
    }
};
</script>

<style scoped>
.folder-tree {
    list-style-type: none;
    padding-left: 20px;
}

.node {
    cursor: pointer;
    margin: 5px 0;
    padding: 2px 8px;
    border-radius: 4px;
    user-select: none;
    /* Prevent text selection */
}

.folder-node:hover,
.file-node:hover {
    background-color: #f0f0f0;
}

.folder-node::before {
    content: '▶ ';
    display: inline-block;
    width: 1em;
    transform: rotate(0);
    transition: transform 0.2s ease-in-out;
}

.folder-node[expanded="true"]::before {
    transform: rotate(90deg);
}
</style>
