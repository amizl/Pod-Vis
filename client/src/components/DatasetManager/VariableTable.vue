<template>
  <v-data-table
    :headers='headers'
    :items='variables'
  >
    <template
      slot='items'
      slot-scope='props'
    >
      <tr>
        <td> {{ props.item.name }} </td>
        <td> {{ props.item.type }} </td>
        <td> {{ props.item.description }} </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
  export default {
    props: {
      variables: Array,
    },
    data() {
      return {
        headers: [
          {
            text: 'Variable',
            value: 'variable',
          },
          {
            text: 'Type',
            value: 'type',
          },
          {
            text: 'Description',
            value: 'description',
          },
        ],
      }
    },
  }
</script>

<style scoped>
</style>
