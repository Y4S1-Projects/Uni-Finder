import { Link } from 'react-router-dom';
import DatasetStatus from './DatasetStatus';
import './styles.css';

const FEATURES = [
  {
    title: 'Explainable Recommendations',
    description:
      'Each match includes eligibility reasoning so students understand how criteria map to their profile.',
  },
  {
    title: 'Hybrid Scoring',
    description:
      'Combines ML similarity matching with rule-based eligibility to balance precision and coverage.',
  },
  {
    title: 'Live Data Refresh',
    description:
      'Designed for scheduled scraping and cleaning so new funding opportunities keep flowing into the model.',
  },
];

export default function StudentMatcherPage() {
  return (
    <div className="matcher-landing">
      <section className="matcher-landing__hero">
        <p className="matcher-page__eyebrow">Funding Discovery Workspace</p>
        <h1>Scholarship & Loan Matching</h1>
        <p className="matcher-page__lead">
          Explore the latest education funding opportunities, then jump into the dedicated flows for
          either scholarships or education loans based on your current priority.
        </p>
        <div className="matcher-landing__cta">
          <Link className="matcher-landing__btn matcher-landing__btn--primary" to="/scholarship-matcher/scholarships">
            Explore Scholarships
          </Link>
          <Link className="matcher-landing__btn matcher-landing__btn--ghost" to="/scholarship-matcher/loans">
            Explore Loans
          </Link>
        </div>
        <p className="matcher-landing__meta">Updated weekly • Powered by scraping + ML baseline</p>
      </section>

      <section className="matcher-landing__split">
        <article className="matcher-landing__card">
          <h2>Scholarship Flow</h2>
          <p>
            Ideal for students tracking grants, bursaries, and merit awards. Feed the form with academic
            milestones, need level, and study interests to uncover the closest matches.
          </p>
          <ul>
            <li>Need & merit filters</li>
            <li>Degree level and field alignment</li>
            <li>Deadline prioritization</li>
          </ul>
          <Link className="matcher-landing__btn matcher-landing__btn--secondary" to="/scholarship-matcher/scholarships">
            Launch Scholarship Flow
          </Link>
        </article>

        <article className="matcher-landing__card">
          <h2>Loan Flow</h2>
          <p>
            Tailored for students comparing educational loans. Capture repayment preferences, desired
            ticket size, and collateral readiness to surface viable options fast.
          </p>
          <ul>
            <li>Repayment friendliness scoring</li>
            <li>Interest rate transparency</li>
            <li>Funding amount normalization</li>
          </ul>
          <Link className="matcher-landing__btn matcher-landing__btn--secondary" to="/scholarship-matcher/loans">
            Launch Loan Flow
          </Link>
        </article>
      </section>

      <section className="matcher-landing__features">
        {FEATURES.map((feature) => (
          <article key={feature.title}>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </article>
        ))}
      </section>

      <section className="matcher-landing__update-section">
        <DatasetStatus />
      </section>
    </div>
  );
}

