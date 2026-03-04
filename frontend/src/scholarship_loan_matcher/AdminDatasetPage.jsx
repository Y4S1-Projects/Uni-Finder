import DatasetUpdateControl from './DatasetUpdateControl';
import './styles.css';

export default function AdminDatasetPage() {
  return (
    <div className="matcher-landing">
      <section className="matcher-landing__hero matcher-landing__hero--admin">
        <p className="matcher-page__eyebrow">Admin Workspace</p>
        <h1>Scholarship & Loan Dataset Admin</h1>
        <p className="matcher-page__lead">
          This page is intended for administrators who manage the live funding datasets.
          Running a full update will trigger web scraping, cleaning, and merging, and can take
          around 10–12 minutes to complete.
        </p>
        <p className="matcher-landing__meta">
          Use this tool only when you need to refresh the underlying data sources.
        </p>
      </section>

      <section className="matcher-landing__split">
        <article className="matcher-landing__card matcher-landing__card--admin">
          <h2>Dataset Update Console</h2>
          <p>
            When you trigger an update, the system will:
          </p>
          <ul>
            <li>Scrape the latest scholarship and loan opportunities from configured sources.</li>
            <li>Clean, deduplicate, and merge them into the central processed datasets.</li>
            <li>Persist the final CSVs that power all scholarship and loan recommendations.</li>
          </ul>
          <p className="matcher-landing__warning">
            This process is resource-intensive and can take approximately 10–12 minutes.
            Avoid running multiple updates back-to-back.
          </p>
        </article>

        <article className="matcher-landing__card matcher-landing__card--admin">
          <DatasetUpdateControl />
        </article>
      </section>
    </div>
  );
}

