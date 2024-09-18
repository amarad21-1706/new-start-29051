import React, { useState, useEffect } from 'react';

function WorkflowView() {
  // State to hold the workflow data and filter values
  const [workflowData, setWorkflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // State for dynamic filter values
  const [areaId, setAreaId] = useState(3);
  const [subareaId, setSubareaId] = useState(1);
  const [fi0, setFi0] = useState(2024);

  // Function to fetch the workflow data
  const fetchData = () => {
    setLoading(true);
    setError(null);

    fetch(`/api/workflow-data?area_id=${areaId}&subarea_id=${subareaId}&fi0=${fi0}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setWorkflowData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  };

  // Fetch data when the component mounts or filter values change
  useEffect(() => {
    fetchData();
  }, [areaId, subareaId, fi0]);  // Dependencies, will re-fetch when these values change

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();  // Prevent page reload
    fetchData();  // Fetch data with the new filters
  };

  return (
    <div>
      <h1>Workflow Data</h1>

      {/* Form for dynamic filtering */}
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Area ID:
            <select value={areaId} onChange={(e) => setAreaId(e.target.value)}>
              <option value="1">Area 1</option>
              <option value="2">Area 2</option>
              <option value="3">Area 3</option>
            </select>
          </label>
        </div>
        <div>
          <label>
            Subarea ID:
            <select value={subareaId} onChange={(e) => setSubareaId(e.target.value)}>
              <option value="1">Subarea 1</option>
              <option value="2">Subarea 2</option>
              <option value="3">Subarea 3</option>
              <option value="4">Subarea 4</option>
              <option value="5">Subarea 5</option>
              <option value="6">Subarea 6</option>
              <option value="7">Subarea 7</option>
              <option value="8">Subarea 8</option>
              <option value="9">Subarea 9</option>
              <option value="10">Subarea 10</option>
              <option value="11">Subarea 11</option>
              <option value="12">Subarea 12</option>
              <option value="13">Subarea 13</option>
              <option value="14">Subarea 14</option>
              <option value="15">Subarea 15</option>
            </select>
          </label>
        </div>
        <div>
        <label>
            FI0:
          <select value={fi0} onChange={(e) => setFi0(e.target.value)}>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="2021">2021</option>
            <option value="2020">2020</option>
          </select>
        </label>
        </div>
        <button type="submit">Fetch Workflow</button>
      </form>

      {/* Display loading spinner */}
      {loading && <div>Loading...</div>}

      {/* Handle error display */}
      {error && <div>Error: {error.message}</div>}

      {/* Display workflow data */}
      <ul>
        {workflowData.map((item) => (
          <li key={item.id}>
            <h2>Document ID: {item.id}</h2>
            <p>Status: {item.record_type || 'No Data'}</p>
            <p>Created On: {item.created_on || 'No Data'}</p>
            <h3>Workflow:</h3>
            <ul>
              {item.workflow.length > 0 ? (
                item.workflow.map((workflow) => (
                  <li key={workflow.workflow_id}>{workflow.workflow_name}</li>
                ))
              ) : (
                <li>No workflow</li>
              )}
            </ul>
            <h3>Step:</h3>
            <ul>
              {item.step.length > 0 ? (
                item.step.map((step) => (
                  <li key={step.step_id}>{step.step_name}</li>
                ))
              ) : (
                <li>No steps</li>
              )}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default WorkflowView;
