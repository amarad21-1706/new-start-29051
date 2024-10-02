<!-- App.svelte -->
<script>
  import { onMount } from 'svelte';

  let data = [];
  let showCreateRecord = false;

  onMount(async () => {
    // Fetch data from Flask-Restful API
    try {
      const response = await fetch('http://localhost:5000/base_data_rest');
      const result = await response.json();
      data = result.data;
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  });

  function showCreateRecordForm() {
    showCreateRecord = true;
  }
</script>

<script>
  import Modal from 'svelte-modal';
  import CreateRecord1 from './CreateRecord1.svelte';

  let data = [];
  let showCreateRecord = false;

  // Fetch data from Flask-Restful API
  async function fetchData() {
    try {
      const response = await fetch('http://localhost:5000/base_data_rest');
      const result = await response.json();
      data = result.data;
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }
  // Function to show the CreateRecord component in a modal
  function createRecord() {
    showCreateRecord = true;
  }
  // Close modal function
  function closeModal() {
    showCreateRecord = false;
  }

  // Initial data fetch
  fetchData();
</script>

<main>
  <h1>Your Svelte-Restful App</h1>
  <!-- Create Record button -->
  <button on:click={createRecord}>Create Record</button>

  {#if showCreateRecord}
    <!-- Show the CreateRecord component in a modal -->
    <Modal bind:show={showCreateRecord} on:close={closeModal}>
      <CreateRecord1 />
    </Modal>
  {/if}


  {#if data.length > 0}
    <!-- Table to display records -->
    <table>
      <!-- Table header -->
      <thead>
        {#each Object.keys(data[0]) as column}
          <th>{column}</th>
        {/each}
      </thead>
      <!-- Table body -->
      <tbody>
        {#each data as row}
          <tr>
            {#each Object.values(row) as value}
              <td>{value}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p>No data available</p>
  {/if}
</main>

<style>
  /* Your styling goes here */
</style>
