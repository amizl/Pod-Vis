<template>
  <v-data-table :headers="headers" :items="variables">
    <template slot="items" slot-scope="props">
      <tr>
        <td>{{ props.item.category }}</td>
        <td>{{ props.item.scale }}</td>
        <td></td>
        <!-- <td>{{ props.item.description }}</td> -->
        <!-- <td>{{ props.item.data_range }}</td> -->
        <!-- <td>{{ props.item.missing }}</td> -->
      </tr>
    </template>
  </v-data-table>
</template>

<script>
export default {
  props: {
    variables: {
      type: Array,
    },
  },
  data() {
    return {
      headers: [
        {
          text: 'Category',
          value: 'category',
        },
        {
          text: 'Scale',
          value: 'scale',
        },
        // {
        //   text: 'Variable',
        //   value: 'variable',
        // },
        // {
        //   text: 'Type',
        //   value: 'type',
        // },
        // {
        //   text: 'Description',
        //   value: 'description',
        // },
        // {
        //   text: 'Data Range',
        //   value: 'data_range',
        // },
        // {
        //   text: 'Missing',
        //   value: 'missing',
        // },
        {
          text: 'Histogram',
          value: 'histogram',
        },
      ],
    };
  },
};
</script>

<style scoped></style>
