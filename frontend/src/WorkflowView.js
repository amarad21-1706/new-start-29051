import React, { useState, useEffect } from 'react';
import './WorkflowView.css';
import Timeline from 'react-calendar-timeline';
import 'react-calendar-timeline/lib/Timeline.css';
import moment from 'moment';

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

  // Fetch workflows, steps, and documents as before
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

  useEffect(() => {
    if (selectedWorkflow === 'all') {
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

  useEffect(() => {
    let queryString = `/api/documents?workflow_id=${selectedWorkflow}&step_id=${selectedStep}&fi0=${fi0}`;
    if (selectedDocument !== '') {
      queryString += `&id=${selectedDocument}`;
    }

    setLoading(true);

    fetch(queryString)
      .then((response) => response.json())
      .then((data) => {
        console.log('Fetched Data:', data);

        if (Array.isArray(data)) {
          setWorkflowData(data);  // Set data for the timeline
          setDocuments(data);     // Set documents for the dropdown
        } else {
          setWorkflowData([]);    // If not an array, set to empty
          setDocuments([]);       // Clear documents dropdown
        }

        setLoading(false);
      })
      .catch((error) => {
        setError(error);
        setLoading(false);
      });
  }, [selectedWorkflow, selectedStep, fi0, selectedDocument]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Build query string with workflow, step, fi0, and document
    let queryString = `/api/documents?workflow_id=${selectedWorkflow}&step_id=${selectedStep}&fi0=${fi0}`;
    if (selectedDocument !== '') {
      queryString += `&id=${selectedDocument}`;
    }

    fetch(queryString)
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setWorkflowData(data);  // Ensure workflowData is an array
        } else {
          setWorkflowData([]);  // If it's not an array, set it to empty array
        }
        setLoading(false);
      })
      .catch((error) => {
        setError(error);
        setLoading(false);
      });
  };

  // Prepare groups and items for the timeline
  const groups = [{ id: 1, title: 'Documents' }];  // One group for simplicity

  const items = workflowData.map((doc) => ({
    id: doc.id,
    group: 1,
    title: `Doc: ${doc.name}`,  // Assuming 'name' is the document name
    start_time: moment(doc.workflows[0]?.date_start),  // Use the actual date_start from first workflow
    end_time: moment(doc.workflows[0]?.date_end)      // Use the actual date_end from first workflow
  }));

  return (
    <div className="container">
      <h1 className="title">Workflow Data</h1>
      <form onSubmit={handleSubmit} className="form-container">
        {/* Workflow, Step, Year, and Document dropdowns as before */}
        <div className="form-group">
          <label htmlFor="workflow-select">Workflow:</label>
          <select
              id="workflow-select"
              value={selectedWorkflow}
              onChange={(e) => setSelectedWorkflow(e.target.value)}
              className="form-control"
          >
            <option value="all">All Workflows</option>
            {workflows.map((wf) => (
                <option key={wf.id} value={wf.id}>
                  {wf.name}
                </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="step-select">Step:</label>
          <select
              id="step-select"
              value={selectedStep}
              onChange={(e) => setSelectedStep(e.target.value)}
              className="form-control"
          >
            <option value="all">All Steps</option>
            {steps.map((step) => (
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
          >
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="2021">2021</option>
            <option value="2020">2020</option>
          </select>
        </div>

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

      {/* Render the Timeline */}
      {!loading && workflowData.length > 0 && (
          <Timeline
              groups={groups}
              items={items}
              defaultTimeStart={moment().startOf('year')}
              defaultTimeEnd={moment().endOf('year')}
          />
      )}
    </div>
  );
}

export default WorkflowView;
