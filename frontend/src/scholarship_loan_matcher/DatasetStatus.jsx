import { useState, useEffect } from 'react';
import { getDatasetStats } from './api';
import './styles.css';

export default function DatasetStatus() {
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const load = async () => {
      setIsLoadingStats(true);
      try {
        const stats = await getDatasetStats();
        if (stats.last_updated) {
          setLastUpdate(stats.last_updated);
        }
      } catch (err) {
        console.error('Failed to load dataset stats:', err);
      } finally {
        setIsLoadingStats(false);
      }
    };
    load();
  }, []);

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

  return (
    <div className="dataset-status">
      <h3 className="dataset-status__title">Funding Dataset Status</h3>
      <p className="dataset-status__body">
        {isLoadingStats
          ? 'Checking the latest update time…'
          : (
            <>
              <strong>Last Updated:</strong>{' '}
              <span className="dataset-status__timestamp">
                {formatDate(lastUpdate)}
              </span>
            </>
          )}
      </p>
      <p className="dataset-status__hint">
        Dataset refreshes are managed from an internal admin page. Students will always see
        results based on the most recently refreshed data.
      </p>
    </div>
  );
}

