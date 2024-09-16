import React, { useState, useEffect } from 'react'; // Correct import for React
import ReactFlow, { Background, Controls } from 'reactflow'; // Importing components from React Flow
import 'reactflow/dist/style.css';

const WorkflowView = ({ documentId }) => {
    const [workflow, setWorkflow] = useState(null);
    const [loading, setLoading] = useState(true); // State to manage loading

    useEffect(() => {
        console.log(`Fetching workflow data for document ID: ${documentId}`); // Debugging log

        fetch(`/workflow/${documentId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Workflow data fetched:', data); // Debugging log
                setWorkflow(data); // Set the fetched workflow data
                setLoading(false); // Set loading to false once data is fetched
            })
            .catch(error => {
                console.error('Error fetching workflow data:', error);
                setLoading(false); // Set loading to false even if there is an error
            });
    }, [documentId]);

    if (loading) {
        return <div>Loading workflow...</div>; // Show loading message
    }

    if (!workflow || !workflow.steps || workflow.steps.length === 0) {
        return <div>No workflow steps found for this document.</div>; // Handle case with no workflow data
    }

    // Prepare nodes and edges for ReactFlow
    const nodes = workflow.steps.map(step => ({
        id: step.step_id.toString(),
        data: { label: step.step_name },
        position: { x: Math.random() * 400, y: Math.random() * 400 } // Random positioning
    }));

    const edges = workflow.steps.slice(1).map((step, index) => ({
        id: `e${workflow.steps[index].step_id}-${step.step_id}`,
        source: workflow.steps[index].step_id.toString(),
        target: step.step_id.toString(),
        type: 'smoothstep',
    }));

    return (
        <div style={{ height: 500 }}>
            <ReactFlow nodes={nodes} edges={edges} fitView>
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
};

export default WorkflowView;
