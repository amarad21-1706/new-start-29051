import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import WorkflowView from './WorkflowView';
import WorkflowGanttChart from './WorkflowGanttChart';
import Menu from './Menu';
import { ErrorBoundary } from 'react-error-boundary';  // Correct package

// Error fallback component to display more useful information
const ErrorFallback = ({ error, resetErrorBoundary }) => (
  <div role="alert">
    <h2>Something went wrong:</h2>
    <pre>{error.message}</pre>
    <button onClick={resetErrorBoundary}>Try again</button>
  </div>
);

const App = () => (
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <Router>
      <div className="App">
        <Menu />
        <Routes>
          <Route path="/" element={<WorkflowView />} />
          <Route path="/react-page" element={<WorkflowGanttChart workflowId={1} />} />
        </Routes>
      </div>
    </Router>
  </ErrorBoundary>
);

export default App;
