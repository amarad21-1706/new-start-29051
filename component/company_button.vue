<template>
  <div class="card mb-2">
    <div class="card-header">
      <!-- Include the CompanyButton component -->
      <CompanyButton :companyName="companyName" :companyRecords="companyRecords" @companySelected="toggleDetails" />
    </div>
    <div class="card-body" v-if="showDetails">
      <table class="table table-striped">
        <!-- ... (rest of your table structure) ... -->
      </table>
    </div>
  </div>
</template>

<script>
// Import the CompanyButton component
import CompanyButton from './CompanyButton.vue';

export default {
  components: {
    CompanyButton, // Register the CompanyButton component
  },
  props: ['companyName', 'companyRecords'],
  data() {
    return {
      showDetails: false,
    };
  },
  methods: {
    toggleDetails() {
      this.showDetails = !this.showDetails;
    },
  },
};
</script>
