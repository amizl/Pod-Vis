<template>
  <v-data-table
    :headers="headers"
    :items="desserts"
    hide-actions
    class="elevation-1"
  >
    <template slot="items" slot-scope="props">
      <td>{{ props.item.name }}</td>
      <td class="text-xs-right">{{ props.item.calories }}</td>
      <td class="text-xs-right">{{ props.item.fat }}</td>
      <td class="text-xs-right">{{ props.item.carbs }}</td>
      <td class="text-xs-right">{{ props.item.protein }}</td>
      <td class="text-xs-right">{{ props.item.iron }}</td>
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
          { text: 'General Disease Severity Measures', value: 'calories' },
          { text: 'Autonomic', value: 'fat' },
          { text: 'Cognitive', value: 'carbs' },
          { text: 'Sleep', value: 'protein' },
          { text: 'Behavior', value: 'iron' },
          { text: 'Disability', value: 'iron' },
          { text: 'Medical Comorbidities', value: 'iron' },
        ],
        desserts: [
          {
            value: false,
            name: 'PPMI',
          },
          {
            value: false,
            name: 'HOME',

          },
        ]
      };
    }
  }
</script>
