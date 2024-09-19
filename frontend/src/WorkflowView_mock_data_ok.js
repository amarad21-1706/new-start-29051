import React, { useState, useEffect } from 'react';
import './styles.css';  // Importing the shared styles
import MetricsGraphs from './MetricsGraphs';  // Import the test chart

function WorkflowView() {
  const [workflowData, setWorkflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [areas, setAreas] = useState([]);
  const [subareas, setSubareas] = useState([]);
  const [selectedArea, setSelectedArea] = useState("");
  const [selectedSubarea, setSelectedSubarea] = useState("");
  const [fi0, setFi0] = useState(2024);  // Default FI0

  // Fetch area and subarea data from the API
  const fetchAreaSubareaData = async () => {
    try {
      const response = await fetch("/api/area-subarea");
      const data = await response.json();
      setAreas(data.areas);
      setSubareas(data.subareas);
    } catch (error) {
      console.error("Error fetching area and subarea data:", error);
    }
  };

  // Fetch workflow data from the API
  const fetchWorkflowData = async () => {
    setLoading(true);
    setError(null);
    setWorkflowData([]);

    try {
      const response = await fetch(`/api/workflow-data?area_id=${selectedArea}&subarea_id=${selectedSubarea}&fi0=${fi0}`);
      if (!response.ok) {
        throw new Error('No response from network');
      }
      const data = await response.json();
      setWorkflowData(data);
    } catch (error) {
      setError(error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch area and subarea data when the component mounts
  useEffect(() => {
    fetchAreaSubareaData();
  }, []);

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    fetchWorkflowData();
  };

  // Filter subareas based on selected area
  const filteredSubareas = subareas.filter(subarea => subarea.area_id === parseInt(selectedArea));

  return (
    <div>
      <h1>Workflow Data</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Area:
            <select value={selectedArea} onChange={(e) => setSelectedArea(e.target.value)}>
              <option value="">Select Area</option>
              {areas.map(([id, name]) => (
                <option key={id} value={id}>{name}</option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label>
            Subarea:
            <select value={selectedSubarea} onChange={(e) => setSelectedSubarea(e.target.value)} disabled={!selectedArea}>
              <option value="">Select Subarea</option>
              {filteredSubareas.map(subarea => (
                <option key={subarea.id} value={subarea.id}>{subarea.name}</option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label>
            Year:
            <select value={fi0} onChange={(e) => setFi0(e.target.value)}>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
              <option value="2021">2021</option>
              <option value="2020">2020</option>
            </select>
          </label>
        </div>

        <button type="submit" disabled={!selectedArea || !selectedSubarea}>Fetch Workflow</button>
      </form>

      {loading && <div>Loading...</div>}
      {error && <div>Error: {error.message}</div>}

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

      {/* Render the test chart here */}
      <MetricsGraphs />
    </div>
  );
}

export default WorkflowView;
