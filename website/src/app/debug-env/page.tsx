"use client"

import React from 'react';

const DebugEnvPage = () => {
  const apiUrl = process.env.NEXT_PUBLIC_SENCHI_API_URL;

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace' }}>
      <h1>Environment Variable Check</h1>
      <p>This page checks the value of the environment variables in the production build.</p>
      <hr style={{ margin: '1rem 0' }} />
      <h2>NEXT_PUBLIC_SENCHI_API_URL:</h2>
      <pre
        style={{
          background: '#f0f0f0',
          padding: '1rem',
          borderRadius: '4px',
          border: '1px solid #ccc',
          wordWrap: 'break-word',
        }}
      >
        {apiUrl ? `"${apiUrl}"` : 'NOT SET or undefined'}
      </pre>
    </div>
  );
};

export default DebugEnvPage; 