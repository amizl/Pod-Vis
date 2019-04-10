<template>
  <v-data-table :headers="headers_" :items="variables">
    <template slot="items" slot-scope="props">
      <tr>
        <td>{{ props.item.category }}</td>
        <td>{{ props.item.scale }}</td>
        <!-- <td v-if="histogram"></td> -->
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
      default: () => [],
    },
    histogram: {
      type: Boolean,
      default: true,
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
          sortable: false,
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
        // {
        //   text: 'Histogram',
        //   value: 'histogram',
        // },
      ],
    };
  },
  computed: {
    headers_() {
      if (!this.histrogram) {
        return this.headers.filter(header => header.value !== 'histogram');
      } else {
        return this.headers;
      }
    },
  },
};
</script>

<style scoped></style>
