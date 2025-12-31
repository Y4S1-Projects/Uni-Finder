import { useMemo, useState } from 'react';
import StudentProfileForm from './StudentProfileForm';
import MatchResults from './MatchResults';
import { requestMatches } from './api';
import './styles.css';

const MATCH_TYPE_COPY = {
  scholarship: {
    eyebrow: 'Scholarship Finder',
    title: 'Scholarship Recommendation Flow',
    lead:
      'Share your academic background, financial context, and goals to surface scholarships that fit your profile.',
    submitLabel: 'Find Scholarships',
    resultsTitle: 'Scholarship Recommendations',
    emptyMessage: 'Submit your profile to discover matching scholarships.',
  },
  loan: {
    eyebrow: 'Loan Finder',
    title: 'Education Loan Recommendation Flow',
    lead:
      'Tell us about your funding requirements, repayment readiness, and study plans to see tailored education loans.',
    submitLabel: 'Find Loans',
    resultsTitle: 'Loan Recommendations',
    emptyMessage: 'Submit your profile to view financing options.',
  },
};

export default function MatcherFlowPage({
  matchType = 'scholarship',
  eyebrow,
  title,
  lead,
  submitLabel,
  resultsTitle,
  emptyMessage,
}) {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const copy = useMemo(() => {
    const defaults = MATCH_TYPE_COPY[matchType] || MATCH_TYPE_COPY.scholarship;
    return {
      eyebrow: eyebrow || defaults.eyebrow,
      title: title || defaults.title,
      lead: lead || defaults.lead,
      submitLabel: submitLabel || defaults.submitLabel,
      resultsTitle: resultsTitle || defaults.resultsTitle,
      emptyMessage: emptyMessage || defaults.emptyMessage,
    };
  }, [matchType, eyebrow, title, lead, submitLabel, resultsTitle, emptyMessage]);

  const handleSubmit = async (profile) => {
    setIsLoading(true);
    setError('');
    try {
      const matches = await requestMatches(profile, {
        topN: 10,
        matchType,
      });
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
        <div className="matcher-page__header">
          <p className="matcher-page__eyebrow">{copy.eyebrow}</p>
          <h1>{copy.title}</h1>
          <p className="matcher-page__lead">{copy.lead}</p>
        </div>

        <StudentProfileForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          submitLabel={copy.submitLabel}
          matchType={matchType}
        />
      </section>

      <section className="matcher-page__panel matcher-page__panel--results">
        <h2>{copy.resultsTitle}</h2>
        <MatchResults
          results={results}
          isLoading={isLoading}
          error={error}
          emptyMessage={copy.emptyMessage}
        />
      </section>
    </div>
  );
}




