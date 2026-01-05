import { Container, Row, Col } from 'react-bootstrap';

const Footer = () => {
  return (
    <footer className="professional-footer">
      <Container>
        <Row className="justify-content-center">
          <Col lg={10}>
            <Row>
              <Col md={4} className="mb-4">
                <h5 className="footer-heading">AI Learning Platform</h5>
                <p className="footer-text">
                  Empowering learners with intelligent educational guidance and personalized learning experiences.
                </p>
              </Col>
              <Col md={4} className="mb-4">
                <h5 className="footer-heading">Quick Links</h5>
                <ul className="footer-links">
                  <li><a href="/">Home</a></li>
                  <li><a href="/recommendations">AI Recommendations</a></li>
                  <li><a href="/profile">Learning Profile</a></li>
                  <li><a href="/keywords">Study Keywords</a></li>
                </ul>
              </Col>
              <Col md={4} className="mb-4">
                <h5 className="footer-heading">Connect With Us</h5>
                <div className="footer-social">
                  <p className="footer-text">Join our community of AI-powered learners</p>
                  <div className="social-icons">
                    <span className="social-icon">📚</span>
                    <span className="social-icon">🤖</span>
                    <span className="social-icon">🎓</span>
                  </div>
                </div>
              </Col>
            </Row>
            <hr className="footer-divider" />
            <Row>
              <Col className="text-center">
                <p className="footer-copyright">
                  &copy; 2024 AI Educational Guidance Platform. Transforming learning through intelligent technology.
                </p>
              </Col>
            </Row>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;