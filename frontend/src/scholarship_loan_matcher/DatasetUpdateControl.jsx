import { useState, useEffect } from 'react';
import { triggerDatasetUpdate, getDatasetStats } from './api';
import './styles.css';

export default function DatasetUpdateControl() {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [currentStats, setCurrentStats] = useState({ scholarships: null, loans: null });
  const [updateStatus, setUpdateStatus] = useState(null); // 'success' | 'error' | null
  const [errorMessage, setErrorMessage] = useState('');
  const [summary, setSummary] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);

  // Load current stats on mount
  useEffect(() => {
    loadCurrentStats();
  }, []);

  const loadCurrentStats = async () => {
    setIsLoadingStats(true);
    try {
      const stats = await getDatasetStats();
      if (stats.success !== false) {
        setCurrentStats({
          scholarships: stats.scholarships !== undefined ? stats.scholarships : null,
          loans: stats.loans !== undefined ? stats.loans : null,
        });
        if (stats.last_updated) {
          setLastUpdate(stats.last_updated);
        }
      }
    } catch (err) {
      console.error('Failed to load dataset stats:', err);
      // Don't show error for stats loading, just keep defaults
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleUpdate = async () => {
    setIsLoading(true);
    setUpdateStatus(null);
    setErrorMessage('');
    setSummary(null);

    try {
      const result = await triggerDatasetUpdate();
      
      if (result.success) {
        setUpdateStatus('success');
        setLastUpdate(result.updated_at || new Date().toISOString());
        setSummary(result.summary || {});
        // Refresh current stats after successful update
        await loadCurrentStats();
      } else {
        setUpdateStatus('error');
        setErrorMessage(result.error || 'Update failed.');
      }
    } catch (err) {
      setUpdateStatus('error');
      setErrorMessage(err.message || 'Failed to update datasets.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const getScholarshipCount = () => {
    if (!summary) return null;
    return summary.cleaner_results?.scholarships?.rows_output || 
           summary.scraper_results?.scholarships_collected || 
           null;
  };

  const getLoanCount = () => {
    if (!summary) return null;
    return summary.cleaner_results?.loans?.rows_output || 
           summary.scraper_results?.loans_collected || 
           null;
  };

  return (
    <div className="dataset-update-control">
      <div className="dataset-update-control__header">
        <h3>Dataset Management</h3>
        <p className="dataset-update-control__description">
          Refresh scholarship and loan data from live sources. This updates the datasets used by the matching engine.
        </p>
      </div>

      <div className="dataset-update-control__actions">
        <button
          className="dataset-update-control__btn"
          onClick={() => setShowConfirm(true)}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="dataset-update-control__spinner">⟳</span>
              Updating...
            </>
          ) : (
            'Update Scholarship & Loan Data'
          )}
        </button>
      </div>

      {showConfirm && !isLoading && (
        <div className="dataset-update-control__modal-backdrop">
          <div className="dataset-update-control__modal">
            <h4 className="dataset-update-control__modal-title">Confirm dataset update</h4>
            <p className="dataset-update-control__modal-body">
              You are about to refresh the live scholarship and loan datasets. This process runs
              a full scraping and cleaning pipeline and can take approximately 10–12 minutes to
              complete. During this time, the server will be busy but students can still browse
              using the existing data.
            </p>
            <p className="dataset-update-control__modal-body">
              Are you sure you want to start the update now?
            </p>
            <div className="dataset-update-control__modal-actions">
              <button
                type="button"
                className="dataset-update-control__modal-btn dataset-update-control__modal-btn--secondary"
                onClick={() => setShowConfirm(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="dataset-update-control__modal-btn dataset-update-control__modal-btn--primary"
                onClick={() => {
                  setShowConfirm(false);
                  handleUpdate();
                }}
              >
                Yes, start update
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Last Updated Timestamp - displayed in place of current dataset */}
      {lastUpdate && (
        <div className="dataset-update-control__status">
          <p className="dataset-update-control__timestamp">
            <strong>Last Updated:</strong> {formatDate(lastUpdate)}
          </p>
        </div>
      )}

      {/* Current Dataset Stats - Hidden for now */}
      {(currentStats.scholarships !== null || currentStats.loans !== null) && (
        <div className="dataset-update-control__current-stats" style={{ display: 'none' }}>
          <p className="dataset-update-control__current-stats-title">
            <strong>Current Dataset:</strong>
          </p>
          <div className="dataset-update-control__stats">
            {currentStats.scholarships !== null && (
              <div className="dataset-update-control__stat-item">
                <span className="dataset-update-control__stat-label">Scholarships:</span>
                <span className="dataset-update-control__stat-value">{currentStats.scholarships}</span>
              </div>
            )}
            {currentStats.loans !== null && (
              <div className="dataset-update-control__stat-item">
                <span className="dataset-update-control__stat-label">Loans:</span>
                <span className="dataset-update-control__stat-value">{currentStats.loans}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {updateStatus === 'success' && summary && (
        <div className="dataset-update-control__success">
          <p className="dataset-update-control__success-message">
            ✓ Dataset update completed successfully!
          </p>
          <p className="dataset-update-control__current-stats-title">
            <strong>Newly added data</strong>
          </p>
          <div className="dataset-update-control__stats">
            {getScholarshipCount() !== null && (
              <div className="dataset-update-control__stat-item">
                <span className="dataset-update-control__stat-label">Scholarships:</span>
                <span className="dataset-update-control__stat-value">{getScholarshipCount()}</span>
              </div>
            )}
            {getLoanCount() !== null && (
              <div className="dataset-update-control__stat-item">
                <span className="dataset-update-control__stat-label">Loans:</span>
                <span className="dataset-update-control__stat-value">{getLoanCount()}</span>
              </div>
            )}
            {summary.duration_seconds && (
              <div className="dataset-update-control__stat-item">
                <span className="dataset-update-control__stat-label">Duration:</span>
                <span className="dataset-update-control__stat-value">
                  {Math.round(summary.duration_seconds)}s
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {updateStatus === 'error' && (
        <div className="dataset-update-control__error">
          <p className="dataset-update-control__error-message">
            ✗ Update failed: {errorMessage}
          </p>
        </div>
      )}
    </div>
  );
}

