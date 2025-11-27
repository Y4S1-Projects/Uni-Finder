export default function MatchResults({ results = [], isLoading, error }) {
  if (isLoading) {
    return <div className="matcher-results__state">Loading recommendations…</div>;
  }

  if (error) {
    return <div className="matcher-results__state matcher-results__state--error">{error}</div>;
  }

  if (!results.length) {
    return <div className="matcher-results__state">Fill the form to see personalized matches.</div>;
  }

  return (
    <div className="matcher-results">
      {results.map((item, index) => (
        <article key={`${item.name}-${index}`} className="matcher-results__card">
          <header>
            <p className="matcher-results__pill">{item.record_type}</p>
            <h3>{item.name}</h3>
          </header>
          <p className="matcher-results__description">{item.description || 'No description available.'}</p>
          <dl>
            {item.program_type && (
              <>
                <dt>Program Type</dt>
                <dd>{item.program_type}</dd>
              </>
            )}
            {item.loan_type && (
              <>
                <dt>Loan Type</dt>
                <dd>{item.loan_type}</dd>
              </>
            )}
            {item.eligibility && (
              <>
                <dt>Eligibility</dt>
                <dd>{item.eligibility}</dd>
              </>
            )}
            {item.funding_amount && (
              <>
                <dt>Funding Amount</dt>
                <dd>LKR {item.funding_amount.toLocaleString()}</dd>
              </>
            )}
            {item.deadline && (
              <>
                <dt>Deadline</dt>
                <dd>{item.deadline}</dd>
              </>
            )}
            {typeof item.final_score === 'number' && (
              <>
                <dt>Match Score</dt>
                <dd>{(item.final_score * 100).toFixed(1)}%</dd>
              </>
            )}
          </dl>

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


