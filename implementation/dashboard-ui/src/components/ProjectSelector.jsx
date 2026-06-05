import React, { useState, useEffect } from 'react';
import {
    ExpandMore as ChevronDown,
    Business as Building2,
    Group as Users,
    Error as AlertCircle,
    Settings
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import './ProjectSelector.css';

const ProjectSelector = () => {
    const [projects, setProjects] = useState([]);
    const [currentProject, setCurrentProject] = useState(null);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('auth_token');

            // If no token, just show a disabled state (don't redirect)
            if (!token) {
                console.warn('ProjectSelector: No auth token found, showing placeholder');
                setError('Authentication required');
                setLoading(false);
                return;
            }

            const response = await fetch('http://localhost:5006/api/projects', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                // Don't throw error - just log and show placeholder
                console.warn('ProjectSelector: API not available yet, showing placeholder');
                setError('Multi-project API not connected');
                setLoading(false);
                return;
            }

            const data = await response.json();
            setProjects(data.projects || []);

            // Restore last selected project or use first one
            const storedProjectId = localStorage.getItem('current_project_id');
            let selectedProject = null;

            if (storedProjectId) {
                selectedProject = data.projects.find(p => p.id === parseInt(storedProjectId));
            }

            if (!selectedProject && data.projects.length > 0) {
                selectedProject = data.projects[0];
            }

            if (selectedProject) {
                setCurrentProject(selectedProject);
                localStorage.setItem('current_project_id', selectedProject.id);
                localStorage.setItem('current_project_slug', selectedProject.slug);
            }

            setLoading(false);
        } catch (err) {
            console.error('Error loading projects:', err);
            setError(err.message);
            setLoading(false);
        }
    };

    const handleProjectChange = (project) => {
        if (project.id === currentProject?.id) {
            setIsDropdownOpen(false);
            return;
        }

        setCurrentProject(project);
        localStorage.setItem('current_project_id', project.id);
        localStorage.setItem('current_project_slug', project.slug);
        setIsDropdownOpen(false);

        // Trigger a custom event that other components can listen to
        window.dispatchEvent(new CustomEvent('projectChanged', { detail: project }));

        // Reload the page to refresh all data
        window.location.reload();
    };

    const getRoleBadgeClass = (role) => {
        const roleMap = {
            'project_owner': 'role-owner',
            'project_admin': 'role-admin',
            'developer': 'role-developer',
            'viewer': 'role-viewer',
            'guest': 'role-guest'
        };
        return roleMap[role] || 'role-default';
    };

    const getRoleDisplayName = (role) => {
        const nameMap = {
            'project_owner': 'Owner',
            'project_admin': 'Admin',
            'developer': 'Developer',
            'viewer': 'Viewer',
            'guest': 'Guest'
        };
        return nameMap[role] || role;
    };

    if (loading) {
        return (
            <div className="project-selector loading">
                <div className="spinner"></div>
                <span>Loading projects...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="project-selector error" title={error}>
                <AlertCircle />
                <span>Projects (API pending)</span>
            </div>
        );
    }

    if (projects.length === 0) {
        return (
            <div className="project-selector empty">
                <Building2 size={18} />
                <span>No projects available</span>
            </div>
        );
    }

    return (
        <div className="project-selector-container">
            <div
                className={`project-selector ${isDropdownOpen ? 'open' : ''}`}
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
                <div className="current-project">
                    <Building2 size={20} className="project-icon" />
                    <div className="project-info">
                        <span className="project-name">{currentProject?.name || 'Select Project'}</span>
                        <span className={`role-badge ${getRoleBadgeClass(currentProject?.my_role)}`}>
                            {getRoleDisplayName(currentProject?.my_role)}
                        </span>
                    </div>
                    <ChevronDown size={20} className={`dropdown-icon ${isDropdownOpen ? 'rotated' : ''}`} />
                </div>

                {currentProject && currentProject.recent_failure_count > 0 && (
                    <div className="project-stats">
                        <span className="failure-count">
                            <AlertCircle size={14} />
                            {currentProject.recent_failure_count} failures (30d)
                        </span>
                    </div>
                )}
            </div>

            {isDropdownOpen && (
                <>
                    <div className="dropdown-overlay" onClick={() => setIsDropdownOpen(false)} />
                    <div className="project-dropdown">
                        <div className="dropdown-header">
                            <Building2 size={16} />
                            <span>Your Projects ({projects.length})</span>
                        </div>

                        <div className="project-list">
                            {projects.map(project => (
                                <div
                                    key={project.id}
                                    className={`project-item ${project.id === currentProject?.id ? 'active' : ''}`}
                                    onClick={() => handleProjectChange(project)}
                                >
                                    <div className="project-item-header">
                                        <Building2 size={18} />
                                        <div className="project-item-info">
                                            <span className="project-item-name">{project.name}</span>
                                            <span className="project-item-slug">/{project.slug}</span>
                                        </div>
                                        <span className={`role-badge ${getRoleBadgeClass(project.my_role)}`}>
                                            {getRoleDisplayName(project.my_role)}
                                        </span>
                                    </div>

                                    {project.description && (
                                        <p className="project-description">{project.description}</p>
                                    )}

                                    <div className="project-item-stats">
                                        {project.recent_failure_count > 0 && (
                                            <span className="stat">
                                                <AlertCircle size={12} />
                                                {project.recent_failure_count} failures
                                            </span>
                                        )}
                                        {project.last_accessed && (
                                            <span className="stat last-accessed">
                                                Last accessed: {new Date(project.last_accessed).toLocaleDateString()}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="dropdown-footer">
                            <button
                                className="manage-projects-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setIsDropdownOpen(false);
                                    navigate('/projects/manage');
                                }}
                            >
                                <Settings size={16} />
                                Manage Projects
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default ProjectSelector;
