import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import './styles.css';

const ADMIN_USERNAMES = ['scholarshipadmin', 'scholarshipadmin2'];

export default function AdminRouteGuard({ children }) {
	const currentUser = useSelector((state) => state.user?.currentUser);
	const isAdmin = currentUser && ADMIN_USERNAMES.includes(currentUser.username);

	if (isAdmin) {
		return children;
	}

	return (
		<div className="matcher-landing" style={{ padding: '3rem 1.5rem', textAlign: 'center' }}>
			<section className="matcher-landing__hero matcher-landing__hero--admin">
				<h2>Access Restricted</h2>
				<p className="matcher-page__lead">
					This page is only available when signed in as the scholarship admin.
					Please sign in with the admin account to manage dataset updates.
				</p>
				<Link className="matcher-landing__btn matcher-landing__btn--primary" to="/signInNew">
					Sign In
				</Link>
			</section>
		</div>
	);
}
