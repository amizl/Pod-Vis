<template>
  <v-data-table
    :headers="headers"
    :items="datasets"
    hide-actions
    class="elevation-1"
  >
    <template slot="items" slot-scope="props">
      <td>{{ props.item.name }}</td>
      <td class="text-xs-right">{{ props.item.race }}</td>
      <td class="text-xs-right">{{ props.item.age }}</td>
      <td class="text-xs-right">{{ props.item.gender }}</td>
    </template>
  </v-data-table>
</template>

<script>
  export default {
    data () {
      return {
        headers: [
          {
            text: 'Datasets',
            align: 'left',
            sortable: false,
            value: 'name'
          },
          { text: 'Race', value: 'race' },
          { text: 'Age', value: 'age' },
          { text: 'Gender', value: 'gender' },
        ],
        datasets: [
          {
            value: true,
            name: 'PPMI',
            race: 'Exists',
            age: 'Exists',
            gender: 'Exists',
          },
          {
            value: false,
            name: 'HOME',
            // race: '',
            age: 'Exists',
            gender: 'Exists',
          },
        ]
      }
    }
  }
</script>