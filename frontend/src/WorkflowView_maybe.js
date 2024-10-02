import React, { useState, useEffect } from 'react';

function WorkflowView() {
  const [workflowData, setWorkflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
          throw new Error('No records found');
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
        setWorkflowData([]);  // Clear data if error occurs
      });
  };

  useEffect(() => {
    fetchData();
  }, [areaId, subareaId, fi0]);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchData();
  };

  return (
    <div>
      <h1>Workflow Data</h1>
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
            </select>
          </label>
        </div>
        <button type="submit">Fetch Data</button>
      </form>

      {loading && <div>Loading...</div>}
      {error && <div>{error.message}</div>}
      <ul>
        {workflowData.map((item) => (
          <li key={item.id}>
            <h2>Document ID: {item.id}</h2>
            <p>Status: {item.record_type || 'No Data'}</p>
            <p>Created On: {item.created_on || 'No Data'}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default WorkflowView;
