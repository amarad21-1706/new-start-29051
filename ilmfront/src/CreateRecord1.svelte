<script>

  let id, company_id, user_id, interval_id, status_id, record_type, data_type, area_id, subarea_id;
  let created_on, updated_on, created_by, fn1, fn2;

  // Function to handle form submission
  async function handleSubmit() {
    // Create an object with the form data
    const formData = {
      id, company_id, user_id, interval_id, status_id, record_type, data_type, area_id, subarea_id,
      created_on, updated_on, created_by, fn1, fn2
    };

    try {
      // Make a request to your API endpoint to create a new record
      const response = await fetch('/base_data_rest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        // Handle success, e.g., redirect or show a success message
        console.log('Record created successfully!');
      } else {
        // Handle error, e.g., show an error message
        console.error('Error creating record:', response.statusText);
      }
    } catch (error) {
      console.error('Error creating record:', error);
    }
  }
</script>

<main>
  {console.log(showCreateRecord)}

  <h1>Create Record</h1>

  <!-- Form for creating a new record -->
  <form on:submit|preventDefault={handleSubmit}>
    <!-- Your form fields go here -->
    <label for="id">ID:</label>
    <input type="text" bind:value={id} />
    <!-- Repeat similar lines for other fields -->
    <label for="fn1">Nr UDD:</label>
    <input type="integer" bind:value={fn1} />
    <label for="fn2">PdR:</label>
    <input type="integer" bind:value={fn2} />

    <button type="submit">Create Record</button>
  </form>
</main>

<style>
  /* Your styling goes here */
</style>
