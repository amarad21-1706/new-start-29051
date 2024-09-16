import React, { useState, useEffect } from 'react'; // Correct import for React

const DocumentsList = ({ onSelectDocument }) => {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    // Fetch all documents from the Flask backend
    fetch('/documents')
      .then(response => response.json())
      .then(data => setDocuments(data))
      .catch(error => console.error('Error fetching documents:', error));
  }, []);

  if (!documents.length) {
    return <div>Loading documents...</div>;
  }

  return (
    <div>
      <h2>All Documents</h2>
      <ul>
        {documents.map(document => (
          <li key={document.document_id}>
            {document.title} - Status: {document.status}
            <button onClick={() => onSelectDocument(document.document_id)}>View Workflow</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentsList;
