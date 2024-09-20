import React, { useState, useEffect } from 'react';
import './WorkflowView.css';

function WorkflowView() {
  const [workflowData, setWorkflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // State for dynamic filter values
  const [workflows, setWorkflows] = useState([]);  // Workflows array
  const [steps, setSteps] = useState([]);          // Steps array
  const [documents, setDocuments] = useState([]);  // Documents array

  const [selectedWorkflow, setSelectedWorkflow] = useState('all');  // Default to 'All Workflows'
  const [selectedStep, setSelectedStep] = useState('all');          // Default to 'All Steps'
  const [selectedDocument, setSelectedDocument] = useState('');
  const [fi0, setFi0] = useState(2024);

  // Fetch all workflows when the component mounts
  useEffect(() => {
    fetch(`/api/get_workflows`)
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data.workflows)) {
          setWorkflows([{ id: 'all', name: 'All Workflows' }, ...data.workflows]);
        } else {
          setWorkflows([{ id: 'all', name: 'All Workflows' }]);
        }
      })
      .catch((error) => setError(error));
  }, []);

  // Fetch steps based on selected workflow
  useEffect(() => {
    if (selectedWorkflow === 'all') {
      // If "All Workflows" is selected, fetch all steps
      fetch(`/api/get_steps`)
        .then((response) => response.json())
        .then((data) => {
          if (Array.isArray(data.steps)) {
            setSteps([{ id: 'all', name: 'All Steps' }, ...data.steps]);
          } else {
            setSteps([{ id: 'all', name: 'All Steps' }]);
          }
        })
        .catch((error) => setError(error));
    } else {
      // Fetch steps related to the selected workflow
      fetch(`/api/get_steps?workflow_id=${selectedWorkflow}`)
        .then((response) => response.json())
        .then((data) => {
          if (Array.isArray(data.steps)) {
            setSteps([{ id: 'all', name: 'All Steps' }, ...data.steps]);
          } else {
            setSteps([{ id: 'all', name: 'All Steps' }]);
          }
        })
        .catch((error) => setError(error));
    }
  }, [selectedWorkflow]);

  // Fetch documents based on selected workflow and step
  useEffect(() => {
    if (selectedWorkflow === 'all' && selectedStep === 'all') {
      fetch(`/api/documents`)
        .then((response) => response.json())
        .then((data) => {
          setDocuments(data);
        })
        .catch((error) => setError(error));
    } else {
      fetch(`/api/documents?workflow_id=${selectedWorkflow}&step_id=${selectedStep}`)
        .then((response) => response.json())
        .then((data) => {
          setDocuments(data);
        })
        .catch((error) => setError(error));
    }
  }, [selectedWorkflow, selectedStep]);

  // Clear steps and documents when the workflow changes
  useEffect(() => {
    setSelectedStep('all');
    setSteps([]);             // Clear steps
    setDocuments([]);         // Clear documents
  }, [selectedWorkflow]);

  // Clear documents when the step changes
  useEffect(() => {
    setSelectedDocument('');  // Clear selected document
    setDocuments([]);         // Clear documents
  }, [selectedStep]);

    // Handle form submission to fetch workflow data
    const handleSubmit = (e) => {
      e.preventDefault();
      setError(null); // Clear previous errors
      setLoading(true);

      // Build query string with workflow, step, and year (fi0)
      let queryString = `/api/documents?workflow_id=${selectedWorkflow}&step_id=${selectedStep}&fi0=${fi0}`;

      fetch(queryString)
        .then((response) => response.json())
        .then((data) => {
          setWorkflowData(data);
          setLoading(false);
        })
        .catch((error) => {
          setError(error); // Set error if fetch fails
          setLoading(false); // Stop loading
        });
    };

  return (
      <div className="container">
          <h1 className="title">Workflow Data</h1>
          <form onSubmit={handleSubmit} className="form-container">
              {/* Workflow Dropdown */}
              <div className="form-group">
                  <label htmlFor="workflow-select">Workflow:</label>
                  <select
                      id="workflow-select"
                      value={selectedWorkflow || 'all'}  // Set 'all' if selectedWorkflow is undefined
                      onChange={(e) => setSelectedWorkflow(e.target.value)}
                      className="form-control"
                  >
                      {/* Add default "All Workflows" option only once */}
                      <option value="all">All Workflows</option>
                      {workflows.length > 0 && workflows.map((wf) => (
                          <option key={wf.id} value={wf.id}>
                              {wf.name}
                          </option>
                      ))}
                  </select>


              </div>

              {/* Step Dropdown */}
              <div className="form-group">
                  <label htmlFor="step-select">Step:</label>
                  <select
                      id="step-select"
                      value={selectedStep || 'all'}  // Set 'all' if selectedStep is undefined
                      onChange={(e) => setSelectedStep(e.target.value)}
                      className="form-control"
                  >
                      {/* Add default "All Steps" option only once */}
                      <option value="all">All Steps</option>
                      {steps.length > 0 && steps.map((step) => (
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

              {/* Document Dropdown */}
              <div className="form-group">
                  <label htmlFor="document-select">Document:</label>
                  <select
                      id="document-select"
                      value={selectedDocument}
                      onChange={(e) => setSelectedDocument(e.target.value)}
                      className="form-control"
                  >
                      <option value="">All Documents</option>
                      {documents.length > 0 &&
                          documents.map((doc) => (
                              <option key={doc.id} value={doc.id}>
                                  {doc.name}
                              </option>
                          ))}
                  </select>
              </div>

              <button type="submit" className="btn btn-primary">
                  Fetch Workflow
              </button>
          </form>


          {/* Loading Spinner */}
          {loading && <div>Loading...</div>}

          {/* Error Handling */}
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
                              {/* Check if workflow is an array and has length > 0 */}
                              {Array.isArray(item.workflow) && item.workflow.length > 0 ? (
                                  item.workflow.map((workflow) => (
                                      <li key={workflow.workflow_id}>{workflow.workflow_name}</li>
                                  ))
                              ) : (
                                  <li>No workflow</li>  // Display "No workflow" if workflow is not an array or empty
                              )}
                          </ul>

                          <h3>Step:</h3>
                          <ul>
                              {/* Check if step is an array and has length > 0 */}
                              {Array.isArray(item.step) && item.step.length > 0 ? (
                                  item.step.map((step) => (
                                      <li key={step.step_id}>{step.step_name}</li>
                                  ))
                              ) : (
                                  <li>No steps</li>  // Display "No steps" if step is not an array or empty
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
