<template>
  <v-treeview
    @update:open='zoomToNode'
    @update:active='zoomToNode'
    activatable
    hoverable
    open-on-click
    transition
    :items='data.children'
    item-key='id'
  >
    <template slot="prepend" slot-scope="{ item, open, leaf }">
      <v-icon :color='color(item.name)'>stop</v-icon>
    </template>
  </v-treeview>
</template>

<script>
function getUniqueNodeId(node) {
  return node
    .ancestors()
    .map(node => node.data.name)
    .reverse()
    .join("-");
}

 export default {
   props: {
     data: {
       type: Object,
       required: true,
     },
     color: {
       type: Function,
       required: true,
     },
     actions: {
       type: Object,
       required: true,
     },
     nodes: {
       type: Array,
       required: true,
     }
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
      console.log(payload);
      const id = payload .pop();
      console.log(id);
      const node = this.getNodeById(id);
      console.log(node);
      if (node) {
        this.actions.updateCurrent(node);
        this.actions.zoomToNode(node);
      }
    },
    /**
     * Given node id, find node.
     */
    getNodeById(id) {
      if (id === undefined) id = 1;
      const node  = this.nodes
        .find( node => node.data.id == id);
      if (node) {
        return node;
      } else {
        return null;
      }
     },
   },
 };
</script>

<style scoped>

</style>
