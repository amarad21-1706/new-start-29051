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

  const [fi0, setFi0] = useState(2025);  // Default year

  // New state for storing the year options
  const [yearOptions, setYearOptions] = useState([]);


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
    fetch(`/api/get_intervals`)
      .then(response => response.json())
      .then(data => {
        const years = data.years || [];
        setFi0(years[0]);  // Set the default selected year to the most recent year
        setYearOptions(years);  // Populate the year dropdown with the last five years
      })
      .catch(error => console.error('Error fetching intervals:', error));
  }, []);


  useEffect(() => {
    let queryString = `/api/documents?workflow_id=${selectedWorkflow}&step_id=${selectedStep}&fi0=${fi0}`;
    if (selectedDocument !== '') {
      queryString += `&id=${selectedDocument}`;
    }

    setLoading(true);

    fetch(queryString)
      .then((response) => response.json())
      .then((data) => {
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
  };

  // Prepare groups and items for the timeline

  // 1. Create a group for each document
  const groups = workflowData.map((doc) => ({
    id: doc.id, // Each document gets its own unique group
    title: `Doc: ${doc.name}`,  // Group title is the document name
  }));

  // Map each document to its own timeline item
  const items = workflowData.map((doc) => ({
    id: doc.id,
    group: doc.id,
    title: `
      Doc: ${doc.name} 
      Number: ${doc.number_of_doc || "N/A"} 
      Area ID: ${doc.area_id || "N/A"} 
      Date: ${doc.date_of_doc ? moment(doc.date_of_doc).format('YYYY-MM-DD') : "N/A"} 
      Updated on: ${doc.updated_on ? moment(doc.updated_on).format('YYYY-MM-DD') : "N/A"} 
      Workflow: ${doc.workflows[0]?.workflow_name || "N/A"} 
      Step: ${doc.workflows[0]?.step_name || "N/A"}
    `,  // Tooltip content, including workflow and step
    start_time: moment(doc.workflows[0]?.date_start),
    end_time: moment(doc.workflows[0]?.date_end),
    itemProps: {
      'data-tip': `Document: ${doc.name} - Start: ${moment(doc.workflows[0]?.date_start).format('LL')} - End: ${moment(doc.workflows[0]?.date_end).format('LL')}`,
    }
  }));

  const handleItemClick = (itemId) => {
    console.log("Item selected:", itemId);  // Debugging
    const selectedDocument = workflowData.find(doc => doc.id === itemId);
    if (selectedDocument) {
      const documentId = selectedDocument.id;
      const adminUrl = `/open_admin_4/bdocuments_view/edit/?id=${documentId}&url=%2Fopen_admin_4%2Fbdocuments_view%2F`;

      console.log("Navigating to:", adminUrl);  // Debugging

      // Use window.location to navigate to the admin page
      window.location.href = adminUrl;
    } else {
      console.error("Document not found.");
    }
  };

  return (
    <div className="container">
      <h1 className="title">Workflow Data</h1>

      {/* Filter Form */}
      <form onSubmit={handleSubmit} className="form-container">
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

        {/* Year Dropdown */}
        <div className="form-group">
          <label htmlFor="year-select">Year (FI0):</label>
          <select
            id="year-select"
            value={fi0}
            onChange={(e) => setFi0(e.target.value)}
            className="form-control"
          >
            {yearOptions.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
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
            {documents.map((doc) => (
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
          onItemClick={(itemId) => handleItemClick(itemId)}  // Use onItemClick
          itemRenderer={({ item, itemContext, getItemProps, getResizeProps }) => (
            <div {...getItemProps(item.itemProps)}>
              <div data-tip={item.title}>{itemContext.title}</div>
            </div>
          )}
        />
      )}
    </div>
  );
}

export default WorkflowView;
