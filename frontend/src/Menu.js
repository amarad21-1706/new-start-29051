import React from 'react';
import { Link } from 'react-router-dom';  // Import Link from react-router-dom

function Menu() {
  return (
    <nav>
      <ul>
        {/* Static link to the Gantt chart page */}
        <li>
          <Link to="/react-page">Workflow Data</Link>
        </li>

        {/* You can add more menu items here */}
        <li>
          <Link to="/">Home</Link>
        </li>
      </ul>
    </nav>
  );
}

export default Menu;
