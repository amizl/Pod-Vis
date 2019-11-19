<template>
  <v-treeview
    :items="data.children"
    activatable
    hoverable
    open-on-click
    transition
    item-key="id"
    @update:open="zoomToNode"
    @update:active="zoomToNode"
  >
    <template v-slot:prepend="{ item }">
      <v-icon
        :color="item.name in color ? color[item.name] : colorScale(item.name)"
        >stop</v-icon
      >
    </template>
  </v-treeview>
</template>

<script>
// function getUniqueNodeId(node) {
//   return node
//     .ancestors()
//     .map(node => node.data.name)
//     .reverse()
//     .join('-');
// }

export default {
  props: {
    data: {
      type: Object,
      required: true,
    },
    colorScale: {
      type: Function,
      required: true,
    },
    color: {
      type: Object,
      required: false,
      default: () => {},
    },
    actions: {
      type: Object,
      required: true,
    },
    nodes: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      active: [],
      tree: [],
      open: [],
    };
  },
  methods: {
    /**
     * Based on Node ID emitted from v-treeview's open event,
     * zoom to given node.
     */
    zoomToNode(payload) {
      const id = payload.pop();
      const node = this.getNodeById(id);
      if (node) {
        this.actions.updateCurrent(node);
        this.actions.zoomToNode(node);
      }
    },
    /**
     * Given node id, find node.
     */
    getNodeById(nodeId) {
      let id = nodeId || 0;

      const node = this.nodes.find(node => node.data.id == id);
      if (node) {
        return node;
      } else {
        return null;
      }
    },
  },
};
</script>

<style scoped></style>
