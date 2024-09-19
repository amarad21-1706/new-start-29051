import React from 'react';
import WorkflowView from './WorkflowView';
import { ErrorBoundary } from 'react-error-boundary';  // Error boundary for safe error handling

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
    <div className="App">
      <WorkflowView />
    </div>
  </ErrorBoundary>
);

export default App;
