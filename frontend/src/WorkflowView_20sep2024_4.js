import React, { useState, useEffect } from 'react';
import './WorkflowView.css';

function WorkflowView() {
  // State for data and filter inputs
  const [workflowData, setWorkflowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // State for dynamic filter values (document, workflow, step, fi0)
  const [documents, setDocuments] = useState([]);  // Ensure it's initialized as an empty array
  const [workflows, setWorkflows] = useState([]);  // Same for workflows
  const [steps, setSteps] = useState([]);          // Same for steps

  const [selectedDocument, setSelectedDocument] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [selectedStep, setSelectedStep] = useState('');
  const [fi0, setFi0] = useState(2024);

  // Fetch documents when the component mounts
  useEffect(() => {
    fetch(`/api/documents`)
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setDocuments(data);  // Set data if it's an array
        } else {
          setDocuments([]);  // Otherwise, reset to an empty array
        }
      })
      .catch((error) => setError(error));
  }, []);  // Empty dependency array means this will run on component mount

  // Fetch workflows when a document is selected
  useEffect(() => {
    if (selectedDocument) {
      fetch(`/api/get_workflows?base_data_id=${selectedDocument}`)
        .then((response) => response.json())
        .then((data) => {
          if (Array.isArray(data.workflows)) {
            setWorkflows(data.workflows);
          } else {
            setWorkflows([]);
          }
        })
        .catch((error) => setError(error));
    } else {
      setWorkflows([]);  // Clear workflows when document is deselected
    }
  }, [selectedDocument]);

  // Fetch steps when a workflow is selected
  useEffect(() => {
    if (selectedWorkflow) {
      fetch(`/api/get_steps?workflow_id=${selectedWorkflow}`)
        .then((response) => response.json())
        .then((data) => {
          if (Array.isArray(data.steps)) {
            setSteps(data.steps);  // Populate steps dropdown
          } else {
            setSteps([]);  // Clear steps if no data
          }
        })
        .catch((error) => setError(error));
    } else {
      setSteps([]);  // Clear steps when no workflow is selected
    }
  }, [selectedWorkflow]);


  // Clear workflow and step data when the document changes
  useEffect(() => {
    setSelectedWorkflow('');  // Clear selected workflow
    setSelectedStep('');      // Clear selected step
    setWorkflows([]);         // Clear workflows
    setSteps([]);             // Clear steps
  }, [selectedDocument]);

  // Handle form submission to fetch workflow data
  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null); // Clear previous errors
    setLoading(true);

    fetch(`/api/workflow-data?base_data_id=${selectedDocument}&workflow_id=${selectedWorkflow}&step_id=${selectedStep}&fi0=${fi0}`)
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
          <div className="form-group">
            <label htmlFor="document-select">Document:</label>
            <select
                id="document-select"
                value={selectedDocument}
                onChange={(e) => setSelectedDocument(e.target.value)}
                className="form-control"
            >
              <option value="">All Documents</option>
              {/* Default option for all documents */}
              {Array.isArray(documents) && documents.length > 0 && documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.name}
                  </option>
              ))}
            </select>
          </div>


          <div className="form-group">
            <label htmlFor="workflow-select">Workflow:</label>
            <select id="workflow-select" value={selectedWorkflow} onChange={(e) => setSelectedWorkflow(e.target.value)}
                    className="form-control">
              <option value="" disabled>Select a Workflow</option>
              {workflows.length > 0 && workflows.map((wf) => (
                  <option key={wf.id} value={wf.id}>
                    {wf.name}
                  </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="step-select">Step:</label>
            <select id="step-select" value={selectedStep} onChange={(e) => setSelectedStep(e.target.value)}
                    className="form-control">
              <option value="" disabled>Select a Step</option>
              {steps.length > 0 && steps.map((step) => (
                  <option key={step.id} value={step.id}>
                    {step.name}
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

          <button type="submit" className="btn btn-primary">
            Fetch Workflow
          </button>
        </form>

        {/* Loading spinner */
        }
        {
            loading && <div>Loading...</div>
        }

        {/* Error handling */
        }
        {
            error && <div className="error">Error: {error.message}</div>
        }

        {/* Display workflow data */
        }
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
)
  ;
}

export default WorkflowView;
