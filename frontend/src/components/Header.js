// // src/components/Header.js
// import React from 'react';
// import { Link } from 'react-router-dom';

// const Header = () => {
//   return (
//     <header>
//       <nav>
//         <Link to="/">Home</Link>
//         <Link to="/signin">Sign In</Link>
//         <Link to="/recommendations">Recommendations</Link>
//       </nav>
//     </header>
//   );
// };

// export default Header;
// src/components/Header.js
import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Navbar, Nav, Container, Button } from "react-bootstrap";

const Header = () => {
	const [scrolled, setScrolled] = useState(false);
	const location = useLocation();
	const isHomePage = location.pathname === "/";

	useEffect(() => {
		const handleScroll = () => {
			const isScrolled = window.scrollY > 100;
			setScrolled(isScrolled);
		};

		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, []);

	const navbarStyle = {
		background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
		backdropFilter: "blur(10px)",
		transition: "all 0.3s ease",
		position: "fixed",
		width: "100%",
		zIndex: 1030,
		boxShadow: "0 2px 20px rgba(0,0,0,0.1)",
	};

	return (
		<Navbar expand='lg' variant='dark' style={navbarStyle} className='fixed-top'>
			<Container>
				<Navbar.Brand as={Link} to='/' className='fw-bold d-flex align-items-center'>
					<span
						style={{
							fontSize: isHomePage ? "1.1rem" : "1.1rem",
							marginRight: isHomePage ? "0.3rem" : "0.3rem",
							background: "rgba(255,255,255,0.2)",
							padding: isHomePage ? "0.2rem" : "0.2rem",
							borderRadius: isHomePage ? "6px" : "6px",
							backdropFilter: "blur(10px)",
						}}>
						🎓
					</span>
					<span style={{ fontSize: isHomePage ? "1rem" : "1rem" }}>UniFinder </span>
				</Navbar.Brand>

				<Navbar.Toggle aria-controls='basic-navbar-nav' />
				<Navbar.Collapse id='basic-navbar-nav'>
					<Nav className='ms-auto align-items-center'>
						<Nav.Link
							as={Link}
							to='/'
							className='fw-semibold mx-1'
							style={{
								color: "rgba(255,255,255,0.9)",
								transition: "color 0.3s ease",
								fontSize: isHomePage ? "0.9rem" : "0.9rem",
							}}>
							Home
						</Nav.Link>
						<Nav.Link
							as={Link}
							to='/keywords'
							className='fw-semibold mx-1'
							style={{
								color: "rgba(255,255,255,0.9)",
								transition: "color 0.3s ease",
								fontSize: isHomePage ? "0.9rem" : "0.9rem",
							}}>
							Solutions
						</Nav.Link>
						<Nav.Link
							as={Link}
							to='/recommendations'
							className='fw-semibold mx-1'
							style={{
								color: "rgba(255,255,255,0.9)",
								transition: "color 0.3s ease",
								fontSize: isHomePage ? "0.9rem" : "0.9rem",
							}}>
							Recommendations
						</Nav.Link>
						<Nav.Link
							as={Link}
							to='/degree-recommendations'
							className='fw-semibold mx-1'
							style={{
								color: "rgba(255,255,255,0.9)",
								transition: "color 0.3s ease",
								fontSize: isHomePage ? "0.9rem" : "0.9rem",
							}}>
							Degrees
						</Nav.Link>
						<Nav.Link
							as={Link}
							to='/career'
							className='fw-semibold mx-1'
							style={{
								color: "rgba(255,255,255,0.9)",
								transition: "color 0.3s ease",
								fontSize: isHomePage ? "0.9rem" : "0.9rem",
							}}>
							Career
						</Nav.Link>
						<Nav.Link
							as={Link}
							to='/all'
							className='fw-semibold mx-1'
							style={{
								color: "rgba(255,255,255,0.9)",
								transition: "color 0.3s ease",
								fontSize: isHomePage ? "0.9rem" : "0.9rem",
							}}>
							Reviews
						</Nav.Link>
						<Nav.Link
							as={Link}
							to='/budget-optimizer-new'
							className='fw-semibold mx-1'
							style={{
								color: "rgba(255,255,255,0.9)",
								transition: "color 0.3s ease",
								fontSize: isHomePage ? "0.9rem" : "0.9rem",
							}}>
							💰 Budget
						</Nav.Link>

						<div className='d-flex ms-2'>
							<Button
								as={Link}
								to='/signInNew'
								variant='outline-light'
								size='sm'
								className='me-1'
								style={{
									borderRadius: isHomePage ? "15px" : "12px",
									padding: isHomePage ? "0.25rem 0.6rem" : "0.2rem 0.5rem",
									fontWeight: "600",
									borderWidth: "1px",
									fontSize: isHomePage ? "0.8rem" : "0.8rem",
								}}>
								Sign In
							</Button>
							<Button
								as={Link}
								to='/signUp'
								variant='light'
								size='sm'
								style={{
									borderRadius: isHomePage ? "15px" : "12px",
									padding: isHomePage ? "0.25rem 0.6rem" : "0.2rem 0.5rem",
									fontWeight: "600",
									color: "#667eea",
									fontSize: isHomePage ? "0.8rem" : "0.8rem",
								}}>
								Sign Up
							</Button>
						</div>
					</Nav>
				</Navbar.Collapse>
			</Container>
		</Navbar>
	);
};

export default Header;
