<template>
    <div class="folder-tree">
        <ul class="list-group">
            <li v-for="(node, index) in treeData" :key="node.id">
                <div :class="['node', { 
                        'folder-node': node.type === 'folder', 
                        'file-node': node.type === 'file' || node.type === 'database', 
                        'top-level-node': index === 0,
                        'expanded': node.expanded }]"

                    @click="toggleNode(node)">
                    <span v-if="node.type === 'folder'">{{ node.expanded ? '📂' : '📁' }}</span>
                    <span v-else-if="node.type === 'database'">🗄️</span>
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
            type: Object,
            required: true
        }
    },
    methods: {
        toggleNode(node) {
            if (node.type === 'folder' || node.type === 'database') {
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
    padding-left: 10px;
}

.list-group {
    padding-left: 5px;
}

.node {
    display: flex;
    align-items: center;
    cursor: pointer;
    margin: 5px 0;
    padding: 2px 0px;
    border-radius: 4px;
    user-select: none;
}

/* Adjust padding for first-level nodes */
.top-level-node .node {
    padding-left: 0;
    padding-left: 0px;
}

.folder-node:hover,
.file-node:hover {
    background-color: #f0f0f0;
}

/* Use data attribute for expanded state */
.folder-node::before {
    content: '▶';
    display: inline-block;
    width: 1em;
    margin-right: 5px;
    transition: transform 0.2s ease-in-out;
}

.folder-node.expanded::before { /* Apply rotation when the node is expanded */
    transform: rotate(90deg);
}

/* Proper alignment of the icons and text */
.node span:first-child {
    margin-right: 5px;
}
</style>