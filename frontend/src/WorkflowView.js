import React, { useState, useEffect } from 'react';
import MetricsGraphs from './MetricsGraphs';

function WorkflowView() {
  const [selectedArea, setSelectedArea] = useState("");
  const [selectedSubarea, setSelectedSubarea] = useState("");
  const [fi0, setFi0] = useState(2024);  // Default year (fi0)

  const [areas, setAreas] = useState([]);
  const [subareas, setSubareas] = useState([]);

  useEffect(() => {
    // Fetch area and subarea data from the API
    const fetchAreaSubareaData = async () => {
      try {
        const response = await fetch("/api/area-subarea");
        const data = await response.json();
        setAreas(data.areas);
        setSubareas(data.subareas);
      } catch (error) {
        console.error("Error fetching area and subarea data:", error);
      }
    };

    fetchAreaSubareaData();
  }, []);

  const filteredSubareas = subareas.filter(subarea => subarea.area_id === parseInt(selectedArea));

  return (
    <div>
      <h1>Workflow Data</h1>

      <form>
        <div>
          <label>
            Area:
            <select value={selectedArea} onChange={(e) => setSelectedArea(e.target.value)}>
              <option value="">Select Area</option>
              {areas.map(([id, name]) => (
                <option key={id} value={id}>{name}</option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label>
            Subarea:
            <select value={selectedSubarea} onChange={(e) => setSelectedSubarea(e.target.value)} disabled={!selectedArea}>
              <option value="">Select Subarea</option>
              {filteredSubareas.map(subarea => (
                <option key={subarea.id} value={subarea.id}>{subarea.name}</option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label>
            Year:
            <select value={fi0} onChange={(e) => setFi0(e.target.value)}>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
              <option value="2021">2021</option>
              <option value="2020">2020</option>
            </select>
          </label>
        </div>
      </form>

      {/* Pass selectedArea, selectedSubarea, and fi0 as props to MetricsGraphs */}
      <MetricsGraphs selectedArea={selectedArea} selectedSubarea={selectedSubarea} selectedYear={fi0} />
    </div>
  );
}

export default WorkflowView;
