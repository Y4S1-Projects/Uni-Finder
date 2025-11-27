import { useState } from 'react';
import StudentProfileForm from './StudentProfileForm';
import MatchResults from './MatchResults';
import { requestMatches } from './api';
import './styles.css';

export default function StudentMatcherPage() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (profile) => {
    setIsLoading(true);
    setError('');
    try {
      const matches = await requestMatches(profile, 6);
      setResults(matches);
    } catch (err) {
      setResults([]);
      setError(err.message || 'Unable to fetch matches right now.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="matcher-page">
      <section className="matcher-page__panel">
        <header>
          <p className="matcher-page__eyebrow">December Demo</p>
          <h1>Scholarship & Loan Matcher</h1>
          <p className="matcher-page__lead">
            Provide a snapshot of the student’s academic profile and funding needs to generate
            scholarships and loans best aligned with their goals.
          </p>
        </header>

        <StudentProfileForm onSubmit={handleSubmit} isLoading={isLoading} />
      </section>

      <section className="matcher-page__panel matcher-page__panel--results">
        <h2>Recommended Opportunities</h2>
        <MatchResults results={results} isLoading={isLoading} error={error} />
      </section>
    </div>
  );
}


