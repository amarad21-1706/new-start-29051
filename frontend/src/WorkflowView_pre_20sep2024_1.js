import React, { useState, useEffect } from 'react';
import './WorkflowView.css'; // Import custom CSS for styling

function WorkflowView() {
  // State for workflow data and filter inputs
  const [workflowData, setWorkflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // State for dynamic filter values (area, subarea, fi0)
  const [areas, setAreas] = useState([]);
  const [subareas, setSubareas] = useState([]);
  const [selectedArea, setSelectedArea] = useState('');
  const [filteredSubareas, setFilteredSubareas] = useState([]);  // Stores the filtered subareas based on selected area
  const [selectedSubarea, setSelectedSubarea] = useState('');
  const [fi0, setFi0] = useState(2024);

  // Fetch the list of areas and subareas from the server
  useEffect(() => {
    fetch('/api/area-subarea')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch area and subarea data');
        }
        return response.json();
      })
      .then(data => {
        const areasList = data.areas.map(([id, name]) => ({ id, name }));
        setAreas(areasList);
        setSubareas(data.subareas); // Load subareas once the API responds
      })
      .catch(error => setError(error));
  }, []);

  // Update filtered subareas when an area is selected
  useEffect(() => {
    if (selectedArea) {
      const areaSubareas = subareas.filter(subarea => subarea.area_id === parseInt(selectedArea));
      setFilteredSubareas(areaSubareas);
    } else {
      setFilteredSubareas([]); // Reset if no area is selected
    }
  }, [selectedArea, subareas]);

  // Clear workflow data when any filter changes
  useEffect(() => {
    setWorkflowData([]); // Clear the current workflow list
  }, [selectedArea, selectedSubarea, fi0]);

  // Function to fetch the workflow data based on selected filters
  const fetchData = () => {
    setLoading(true);
    setError(null);

    fetch(`/api/workflow-data?area_id=${selectedArea}&subarea_id=${selectedSubarea}&fi0=${fi0}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch workflow data');
        }
        return response.json();
      })
      .then((data) => {
        setWorkflowData(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error);
        setLoading(false);
      });
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page reload
    fetchData(); // Fetch data with the new filters
  };

  return (
    <div className="container">
      <h1 className="title">Workflow Data</h1>

      {/* Filter form */}
      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label htmlFor="area-select">Area:</label>
          <select
            id="area-select"
            value={selectedArea}
            onChange={(e) => setSelectedArea(e.target.value)}
            className="form-control"
            required
          >
            <option value="">Select an Area</option>
            {areas.map((area) => (
              <option key={area.id} value={area.id}>
                {area.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="subarea-select">Subarea:</label>
          <select
            id="subarea-select"
            value={selectedSubarea}
            onChange={(e) => setSelectedSubarea(e.target.value)}
            className="form-control"
            required
          >
            <option value="">Select a Subarea</option>
            {filteredSubareas.map((subarea) => (
              <option key={subarea.id} value={subarea.id}>
                {subarea.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="year-select">Year (FI0):</label>
          <select
            id="year-select"
            value={fi0}
            onChange={(e) => setFi0(e.target.value)}
            className="form-control"
            required
          >
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="2021">2021</option>
            <option value="2020">2020</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary">Fetch Workflow</button>
      </form>

      {/* Loading spinner */}
      {loading && <div>Loading...</div>}

      {/* Error handling */}
      {error && <div className="error">Error: {error.message}</div>}

      {/* Display workflow data */}
      <ul className="workflow-list">
        {workflowData.length > 0 ? (
          workflowData.map((item) => (
            <li key={item.id} className="workflow-item">
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
          ))
        ) : (
          !loading && <p>No workflow data available</p>
        )}
      </ul>
    </div>
  );
}

export default WorkflowView;
