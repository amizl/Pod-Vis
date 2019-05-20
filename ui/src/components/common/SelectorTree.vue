<template>
  <v-treeview :items="items"></v-treeview>
</template>

<script>
export default {
  name: 'SelectorTree',
  data: () => ({
    items: [
        {
            id: 1,
            name: 'Outcome variables',
            children: [
                { id: 2, name: 'Motor' },
                { id: 3, name: 'Autonomic' },
                { id: 4, name: 'Cognitive' },
                { id: 5, name: 'Sleep' }
            ]
        }
    ]
  })
}
</script>

<style scoped></style>
