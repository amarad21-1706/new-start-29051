import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import WorkflowView from './WorkflowView';
import WorkflowGanttChart from './WorkflowGanttChart';
import Menu from './Menu';
import { ErrorBoundary } from 'react-error-boundary';  // Correct package

const App = () => (
  <ErrorBoundary fallback={<h1>Something went wrong.</h1>}>
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
