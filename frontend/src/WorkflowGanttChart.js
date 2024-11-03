import React, { useEffect, useState } from 'react';
import { Timeline } from 'react-gantt-timeline';
import Modal from 'react-modal';  // For task detail modals

Modal.setAppElement('#root');  // Move this out of useEffect to ensure it is called once globally

const WorkflowGanttChart = ({ workflowId }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/workflows/${workflowId}`);
        const data = await response.json();

        const formattedTasks = data.tasks.map(task => ({
          id: task.id,
          name: task.name,
          start: new Date(task.start_date),
          end: new Date(task.end_date),
          status: task.status,
          assignee: task.assignee,
        }));

        setTasks(formattedTasks);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching workflow data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, [workflowId]);

  const onTaskClick = (task) => {
    setSelectedTask(task);
  };

  const closeModal = () => {
    setSelectedTask(null);
  };

  const markTaskAsCompleted = () => {
    if (selectedTask) {
      const updatedData = { status: 'completed' };
      updateTask(selectedTask.id, updatedData);
      closeModal();
    }
  };

  const updateTask = async (taskId, updatedData) => {
    const response = await fetch(`/api/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedData),
    });

    if (response.ok) {
      console.log('Task updated successfully');
      // Optionally refetch data or update state here
    } else {
      console.error('Error updating task');
    }
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h2>Workflow Gantt Chart</h2>
      <Timeline data={tasks} onSelectItem={onTaskClick} />

      {selectedTask && (
        <Modal isOpen={!!selectedTask} onRequestClose={closeModal}>
          <h3>{selectedTask.name}</h3>
          <p>Assignee: {selectedTask.assignee}</p>
          <p>Status: {selectedTask.status}</p>
          <button onClick={markTaskAsCompleted}>Mark as Completed</button>
          <button onClick={closeModal}>Close</button>
        </Modal>
      )}
    </div>
  );
};

export default WorkflowGanttChart;
