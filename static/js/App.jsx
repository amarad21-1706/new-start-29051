
import React, { useState } from 'react'; // Correct import for React
import DocumentsList from './DocumentsList'; // Import your React components
import WorkflowView from './WorkflowView';

const App = () => {
  // State to manage which component to show
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);

  // Handle document selection
  const handleSelectDocument = (documentId) => {
    setSelectedDocumentId(documentId); // Set the selected document ID
  };

  return (
    <div>
      <h1>Document Management</h1>
      {selectedDocumentId ? (
        // Render WorkflowView if a document is selected
        <div>
          <button onClick={() => setSelectedDocumentId(null)}>Back to All Documents</button>
          <WorkflowView documentId={selectedDocumentId} />
        </div>
      ) : (
        // Render DocumentsList if no document is selected
        <DocumentsList onSelectDocument={handleSelectDocument} />
      )}
    </div>
  );
};

export default App;
