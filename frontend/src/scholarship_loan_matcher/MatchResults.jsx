export default function MatchResults({
  results = [],
  isLoading,
  error,
  emptyMessage = 'Fill the form to see personalized matches.',
}) {
  if (isLoading) {
    return <div className="matcher-results__state">Loading recommendations…</div>;
  }

  if (error) {
    return <div className="matcher-results__state matcher-results__state--error">{error}</div>;
  }

  if (!results.length) {
    return <div className="matcher-results__state">{emptyMessage}</div>;
  }

  return (
    <div className="matcher-results">
      {results.map((item, index) => (
        <article key={`${item.name}-${index}`} className="matcher-results__card">
          <header className="matcher-results__header">
            <div className="matcher-results__header-top">
              <p className="matcher-results__pill">{item.record_type}</p>
              {typeof item.final_score === 'number' && (
                <span className="matcher-results__score-badge">
                  {(item.final_score * 100).toFixed(0)}% match
                </span>
              )}
            </div>
            <h3 className="matcher-results__title">{item.name}</h3>
          </header>

          <div className="matcher-results__body">
            <p className="matcher-results__description">
              {item.description || 'No description available.'}
            </p>

            <div className="matcher-results__meta">
              <div className="matcher-results__meta-primary">
                {(item.program_type || item.loan_type) && (
                  <div className="matcher-results__meta-item">
                    <span className="matcher-results__meta-label">Program Type</span>
                    <span className="matcher-results__meta-value">
                      {item.program_type || item.loan_type}
                    </span>
                  </div>
                )}
                {item.funding_amount && (
                  <div className="matcher-results__meta-item">
                    <span className="matcher-results__meta-label">Funding Amount</span>
                    <span className="matcher-results__meta-value">
                      LKR {item.funding_amount.toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="matcher-results__meta-secondary">
                {item.provider && (
                  <div className="matcher-results__meta-item">
                    <span className="matcher-results__meta-label">Organization / University</span>
                    <span className="matcher-results__meta-value">{item.provider}</span>
                  </div>
                )}
                {item.deadline && (
                  <div className="matcher-results__meta-item">
                    <span className="matcher-results__meta-label">Application Deadline</span>
                    <span className="matcher-results__meta-value">{item.deadline}</span>
                  </div>
                )}
                {item.region && (
                  <div className="matcher-results__meta-item">
                    <span className="matcher-results__meta-label">Region</span>
                    <span className="matcher-results__meta-value">{item.region}</span>
                  </div>
                )}
                {item.eligibility && (
                  <div className="matcher-results__meta-item">
                    <span className="matcher-results__meta-label">Key Eligibility</span>
                    <span className="matcher-results__meta-value">{item.eligibility}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {item.eligibility_reasons && (
            <div className="matcher-results__eligibility">
              <h4>
                {item.eligibility_status === 'eligible'
                  ? 'Why you are eligible'
                  : 'Why you may not be fully eligible'}
              </h4>
              <div className="matcher-results__eligibility-columns">
                <div>
                  <h5>Passed conditions</h5>
                  <ul>
                    {(item.eligibility_reasons.passed || []).length === 0 && (
                      <li>No specific passed conditions detected.</li>
                    )}
                    {(item.eligibility_reasons.passed || []).map((reason, i) => (
                      <li key={`pass-${index}-${i}`}>{reason}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5>Failed / doubtful conditions</h5>
                  <ul>
                    {(item.eligibility_reasons.failed || []).length === 0 && (
                      <li>No blocking conditions detected.</li>
                    )}
                    {(item.eligibility_reasons.failed || []).map((reason, i) => (
                      <li key={`fail-${index}-${i}`}>{reason}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {item.application_url && (
            <a
              href={item.application_url}
              target="_blank"
              rel="noreferrer"
              className="matcher-results__link"
            >
              View Details
            </a>
          )}
        </article>
      ))}
    </div>
  );
}


