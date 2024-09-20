import React, { useState, useEffect } from 'react';
import './WorkflowView.css'; // Import custom CSS for styling

function WorkflowView() {
  // State for workflow data and filter inputs
  const [workflowData, setWorkflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // State for dynamic filter values (area, subarea, fi0, document, workflow, step, deadline)
  const [areas, setAreas] = useState([]);
  const [subareas, setSubareas] = useState([]);
  const [selectedArea, setSelectedArea] = useState('');
  const [filteredSubareas, setFilteredSubareas] = useState([]);  // Stores the filtered subareas based on selected area
  const [selectedSubarea, setSelectedSubarea] = useState('');
  const [fi0, setFi0] = useState(2024);

  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState('');

  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState('');

  const [steps, setSteps] = useState([]);
  const [selectedStep, setSelectedStep] = useState('');

  const [deadlineFrom, setDeadlineFrom] = useState('');
  const [deadlineTo, setDeadlineTo] = useState('');

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

  // Fetch documents from the server to populate the document dropdown
  useEffect(() => {
    fetch('/api/documents')
      .then(response => response.json())
      .then(data => setDocuments(data))
      .catch(error => setError(error));
  }, []);

  // Fetch workflows based on the selected document
  useEffect(() => {
    if (selectedDocument) {
      fetch(`/api/get_workflows?base_data_id=${selectedDocument}`)
        .then(response => response.json())
        .then(data => setWorkflows(data.workflows))
        .catch(error => setError(error));
    } else {
      setWorkflows([]);  // Clear workflows when document is deselected
    }
  }, [selectedDocument]);

  // Fetch steps based on the selected workflow
  useEffect(() => {
    if (selectedWorkflow) {
      fetch(`/api/get_steps?workflow_id=${selectedWorkflow}`)
        .then(response => response.json())
        .then(data => setSteps(data.steps))
        .catch(error => setError(error));
    } else {
      setSteps([]);  // Clear steps when workflow is deselected
    }
  }, [selectedWorkflow]);

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
  }, [selectedArea, selectedSubarea, fi0, selectedDocument, selectedWorkflow, selectedStep, deadlineFrom, deadlineTo]);

  // Function to fetch the workflow data based on selected filters
  const fetchData = () => {
    setLoading(true);
    setError(null);

    const queryParams = new URLSearchParams({
      area_id: selectedArea,
      subarea_id: selectedSubarea,
      fi0,
      document_id: selectedDocument,
      workflow_id: selectedWorkflow,
      step_id: selectedStep,
      deadline_from: deadlineFrom,
      deadline_to: deadlineTo
    }).toString();

    fetch(`/api/workflow-data?${queryParams}`)
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
        {/* Area Dropdown */}
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

        {/* Subarea Dropdown */}
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

        {/* Document Dropdown */}
        <div className="form-group">
          <label htmlFor="document-select">Document:</label>
          <select
            id="document-select"
            value={selectedDocument}
            onChange={(e) => setSelectedDocument(e.target.value)}
            className="form-control"
          >
            <option value="">Select a Document</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.name}
              </option>
            ))}
          </select>
        </div>

        {/* Workflow Dropdown */}
        <div className="form-group">
          <label htmlFor="workflow-select">Workflow:</label>
          <select
            id="workflow-select"
            value={selectedWorkflow}
            onChange={(e) => setSelectedWorkflow(e.target.value)}
            className="form-control"
          >
            <option value="">Select a Workflow</option>
            {workflows.map((workflow) => (
              <option key={workflow.id} value={workflow.id}>
                {workflow.name}
              </option>
            ))}
          </select>
        </div>

        {/* Step Dropdown */}
        <div className="form-group">
          <label htmlFor="step-select">Step:</label>
          <select
            id="step-select"
            value={selectedStep}
            onChange={(e) => setSelectedStep(e.target.value)}
            className="form-control"
          >
            <option value="">Select a Step</option>
            {steps.map((step) => (
              <option key={step.id} value={step.id}>
                {step.name}
              </option>
            ))}
          </select>
        </div>

        {/* Year Dropdown */}
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

        {/* Deadline Range */}
        <div className="form-group">
          <label htmlFor="deadline-from">Deadline From:</label>
          <input
            type="date"
            id="deadline-from"
            value={deadlineFrom}
            onChange={(e) => setDeadlineFrom(e.target.value)}
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label htmlFor="deadline-to">Deadline To:</label>
          <input
            type="date"
            id="deadline-to"
            value={deadlineTo}
            onChange={(e) => setDeadlineTo(e.target.value)}
            className="form-control"
          />
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
