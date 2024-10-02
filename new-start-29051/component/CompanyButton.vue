<template>
  <div>
    <button @click="toggleDetails">{{ companyName }}</button>
    <div v-if="showDetails">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>#</th>
            <th>Record Type</th>
            <th>Created By</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in companyRecords" :key="record.id">
            <th scope="row">{{ record.id }}</th>
            <td>{{ record.record_type }}</td>
            <td>{{ record.created_by }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  props: ['companyName', 'companyRecords'],
  data() {
    return {
      showDetails: false,
    };
  },
  methods: {
    toggleDetails() {
      this.showDetails = !this.showDetails;
      // Emit an event to notify the parent about the company selection
      this.$emit('companySelected', this.companyName, this.companyRecords);
    },
  },
};
</script>

<style scoped>
/* Add your component-specific styles here if needed */
</style>
