import React, { useState, useEffect } from 'react';

const ServiceControl = () => {
  const [services, setServices] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [hiddenServices, setHiddenServices] = useState(() => {
    // Load hidden services from localStorage
    const saved = localStorage.getItem('hiddenServices');
    return saved ? JSON.parse(saved) : [];
  });

  // Service Manager API URL
  const API_URL = 'http://localhost:5007/api/services';

  // Fetch service status
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/status`);
      if (!response.ok) {
        throw new Error('Service Manager API not available');
      }
      const data = await response.json();
      setServices(data);
      setMessage(''); // Clear error message on success
    } catch (error) {
      console.warn('Service Manager API not available on port 5007:', error);
      setMessage('Service Manager API not running (optional feature - use batch files instead)');
      setServices({}); // Clear services
    }
  };

  // Initial fetch and periodic refresh
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Start all services
  const handleStartAll = async () => {
    if (!window.confirm('Start all services? This will start PostgreSQL, AI Analysis, Dashboard API, n8n, and Jenkins.')) {
      return;
    }

    setLoading(true);
    setMessage('Starting all services...');

    try {
      const response = await fetch(`${API_URL}/start-all`, {
        method: 'POST'
      });
      const data = await response.json();
      setMessage('All services started successfully!');
      fetchStatus();
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Stop all services
  const handleStopAll = async () => {
    if (!window.confirm('Stop all services? This will stop all running services.')) {
      return;
    }

    setLoading(true);
    setMessage('Stopping all services...');

    try {
      const response = await fetch(`${API_URL}/stop-all`, {
        method: 'POST'
      });
      const data = await response.json();
      setMessage('All services stopped successfully!');
      fetchStatus();
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Restart all services
  const handleRestartAll = async () => {
    if (!window.confirm('Restart all services? This will stop and then start all services.')) {
      return;
    }

    setLoading(true);
    setMessage('Restarting all services...');

    try {
      const response = await fetch(`${API_URL}/restart-all`, {
        method: 'POST'
      });
      const data = await response.json();
      setMessage('All services restarted successfully!');
      fetchStatus();
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Start individual service
  const handleStartService = async (serviceId) => {
    setLoading(true);
    setMessage(`Starting ${serviceId}...`);

    try {
      const response = await fetch(`${API_URL}/start/${serviceId}`, {
        method: 'POST'
      });
      const data = await response.json();
      setMessage(data.message || `${serviceId} started`);

      // Wait 3 seconds before checking status to ensure service has started
      await new Promise(resolve => setTimeout(resolve, 3000));
      fetchStatus();
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Stop individual service
  const handleStopService = async (serviceId) => {
    setLoading(true);
    setMessage(`Stopping ${serviceId}...`);

    try {
      const response = await fetch(`${API_URL}/stop/${serviceId}`, {
        method: 'POST'
      });
      const data = await response.json();
      setMessage(data.message || `${serviceId} stopped`);

      // Wait 3 seconds before checking status to ensure service has stopped
      await new Promise(resolve => setTimeout(resolve, 3000));
      fetchStatus();
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Hide/Remove service from display
  const handleRemoveService = (serviceId, serviceName) => {
    if (window.confirm(`Hide "${serviceName}" from the control panel?\n\nYou can show it again by clicking "Show Hidden Services" button.`)) {
      const updated = [...hiddenServices, serviceId];
      setHiddenServices(updated);
      localStorage.setItem('hiddenServices', JSON.stringify(updated));
      setMessage(`${serviceName} hidden from control panel`);
    }
  };

  // Show hidden service
  const handleShowService = (serviceId) => {
    const updated = hiddenServices.filter(id => id !== serviceId);
    setHiddenServices(updated);
    localStorage.setItem('hiddenServices', JSON.stringify(updated));
    setMessage('Service restored to control panel');
  };

  // Show all hidden services
  const handleShowAllHidden = () => {
    setHiddenServices([]);
    localStorage.setItem('hiddenServices', JSON.stringify([]));
    setMessage('All services restored');
  };

  // Get visible services (not hidden)
  const visibleServices = Object.entries(services).filter(([id]) => !hiddenServices.includes(id));
  const hiddenServicesData = Object.entries(services).filter(([id]) => hiddenServices.includes(id));

  // Open external service in new tab
  const openExternalService = (url, serviceName) => {
    window.open(url, '_blank');
    setMessage(`Opening ${serviceName}...`);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>🎛️ Service Control Panel</h2>

      {/* Quick Links to External Services */}
      <div style={styles.quickLinks}>
        <h3 style={styles.quickLinksTitle}>🔗 Quick Access</h3>
        <div style={styles.quickLinksButtons}>
          <button
            onClick={() => openExternalService('https://cloud.mongodb.com/', 'MongoDB Atlas')}
            style={{...styles.quickLinkButton, ...styles.mongodbButton}}
            title="Open MongoDB Atlas Dashboard"
          >
            <span style={styles.buttonIcon}>🍃</span>
            <span>MongoDB Atlas</span>
          </button>
          <button
            onClick={() => openExternalService('https://id.atlassian.com/login', 'Jira/Atlassian')}
            style={{...styles.quickLinkButton, ...styles.jiraButton}}
            title="Open Jira/Atlassian Dashboard"
          >
            <span style={styles.buttonIcon}>🔷</span>
            <span>Jira/Atlassian</span>
          </button>
          <button
            onClick={() => openExternalService('https://app.pinecone.io/', 'Pinecone')}
            style={{...styles.quickLinkButton, ...styles.pineconeButton}}
            title="Open Pinecone Dashboard"
          >
            <span style={styles.buttonIcon}>🌲</span>
            <span>Pinecone</span>
          </button>
          <button
            onClick={() => openExternalService('http://localhost:8081', 'Jenkins')}
            style={{...styles.quickLinkButton, ...styles.jenkinsButton}}
            title="Open Jenkins Dashboard"
          >
            <span style={styles.buttonIcon}>⚙️</span>
            <span>Jenkins</span>
          </button>
          <button
            onClick={() => openExternalService('http://localhost:5678', 'n8n')}
            style={{...styles.quickLinkButton, ...styles.n8nButton}}
            title="Open n8n Workflows"
          >
            <span style={styles.buttonIcon}>🔄</span>
            <span>n8n Workflows</span>
          </button>
        </div>
      </div>

      <div style={styles.divider}></div>

      {/* Main Control Buttons */}
      <div style={styles.mainButtons}>
        <button
          onClick={handleStartAll}
          disabled={loading}
          style={{...styles.button, ...styles.startButton}}
        >
          ▶️ START ALL
        </button>
        <button
          onClick={handleStopAll}
          disabled={loading}
          style={{...styles.button, ...styles.stopButton}}
        >
          ⏹️ STOP ALL
        </button>
        <button
          onClick={handleRestartAll}
          disabled={loading}
          style={{...styles.button, ...styles.restartButton}}
        >
          🔄 RESTART ALL
        </button>
      </div>

      {/* Status Message */}
      {message && (
        <div style={styles.message}>
          {message}
        </div>
      )}

      {/* Service Status Table */}
      <div style={styles.serviceList}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Service Status</h3>
          {hiddenServicesData.length > 0 && (
            <button
              onClick={handleShowAllHidden}
              style={{...styles.actionButton, ...styles.showButton}}
            >
              👁️ Show Hidden Services ({hiddenServicesData.length})
            </button>
          )}
        </div>
        <table style={styles.table}>
          <thead>
            <tr>
              <th>Service</th>
              <th>Port</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {visibleServices.map(([id, service]) => (
              <tr key={id}>
                <td>{service.name}</td>
                <td>{service.port}</td>
                <td>
                  <span style={service.running ? styles.running : styles.stopped}>
                    {service.running ? '✅ Running' : '❌ Stopped'}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    {service.running ? (
                      <button
                        onClick={() => handleStopService(id)}
                        disabled={loading}
                        style={{...styles.actionButton, ...styles.stopActionButton}}
                      >
                        ⏹️ Stop
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStartService(id)}
                        disabled={loading}
                        style={{...styles.actionButton, ...styles.startActionButton}}
                      >
                        ▶️ Start
                      </button>
                    )}
                    <button
                      onClick={() => handleRemoveService(id, service.name)}
                      disabled={loading}
                      style={{...styles.actionButton, ...styles.removeButton}}
                      title="Hide this service from control panel"
                    >
                      🗑️ Remove
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Hidden Services Section */}
        {hiddenServicesData.length > 0 && (
          <div style={styles.hiddenSection}>
            <h4>Hidden Services ({hiddenServicesData.length})</h4>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Port</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {hiddenServicesData.map(([id, service]) => (
                  <tr key={id} style={{ opacity: 0.6 }}>
                    <td>{service.name}</td>
                    <td>{service.port}</td>
                    <td>
                      <span style={service.running ? styles.running : styles.stopped}>
                        {service.running ? '✅ Running' : '❌ Stopped'}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => handleShowService(id)}
                        style={{...styles.actionButton, ...styles.showButton}}
                      >
                        👁️ Show
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Help Text */}
      <div style={styles.help}>
        <p><strong>Note:</strong> This panel controls all DDN AI system services.</p>
        <p>Services will be started/stopped in the correct order automatically.</p>
      </div>
    </div>
  );
};

// Styles
const styles = {
  container: {
    padding: '20px',
    maxWidth: '800px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif'
  },
  title: {
    textAlign: 'center',
    color: '#2c3e50',
    marginBottom: '30px'
  },
  mainButtons: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '30px'
  },
  button: {
    padding: '15px 30px',
    fontSize: '16px',
    fontWeight: 'bold',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    transition: 'all 0.3s'
  },
  startButton: {
    backgroundColor: '#27ae60',
    color: 'white'
  },
  stopButton: {
    backgroundColor: '#e74c3c',
    color: 'white'
  },
  restartButton: {
    backgroundColor: '#3498db',
    color: 'white'
  },
  message: {
    textAlign: 'center',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px',
    marginBottom: '20px',
    color: '#2c3e50'
  },
  serviceList: {
    marginTop: '30px'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '15px'
  },
  running: {
    color: '#27ae60',
    fontWeight: 'bold'
  },
  stopped: {
    color: '#e74c3c',
    fontWeight: 'bold'
  },
  actionButton: {
    padding: '5px 15px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '3px',
    cursor: 'pointer',
    fontSize: '13px'
  },
  startActionButton: {
    backgroundColor: '#27ae60'
  },
  stopActionButton: {
    backgroundColor: '#e74c3c'
  },
  removeButton: {
    backgroundColor: '#95a5a6'
  },
  showButton: {
    backgroundColor: '#f39c12'
  },
  hiddenSection: {
    marginTop: '30px',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px',
    border: '2px dashed #ccc'
  },
  help: {
    marginTop: '30px',
    padding: '15px',
    backgroundColor: '#ecf0f1',
    borderRadius: '5px',
    fontSize: '14px'
  },
  quickLinks: {
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '10px',
    border: '2px solid #e0e0e0'
  },
  quickLinksTitle: {
    margin: '0 0 15px 0',
    color: '#2c3e50',
    fontSize: '18px'
  },
  quickLinksButtons: {
    display: 'flex',
    gap: '15px',
    flexWrap: 'wrap',
    justifyContent: 'center'
  },
  quickLinkButton: {
    padding: '12px 24px',
    fontSize: '14px',
    fontWeight: '600',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    color: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
    }
  },
  buttonIcon: {
    fontSize: '20px'
  },
  mongodbButton: {
    background: 'linear-gradient(135deg, #4caf50 0%, #45a049 100%)'
  },
  jiraButton: {
    background: 'linear-gradient(135deg, #0052CC 0%, #0747A6 100%)'
  },
  pineconeButton: {
    background: 'linear-gradient(135deg, #00C9A7 0%, #00B296 100%)'
  },
  jenkinsButton: {
    background: 'linear-gradient(135deg, #D24939 0%, #C43E2F 100%)'
  },
  n8nButton: {
    background: 'linear-gradient(135deg, #EA4B71 0%, #E03A5F 100%)'
  },
  divider: {
    height: '2px',
    backgroundColor: '#e0e0e0',
    margin: '20px 0',
    borderRadius: '2px'
  }
};

export default ServiceControl;