// // src/pages/BestRecommendationPage.js
// import React from 'react';
// import { useLocation } from 'react-router-dom';

// const BestRecommendationPage = () => {
//   const location = useLocation();
//   const { recommendation } = location.state || { recommendation: 'No recommendation available.' };

//   return (
//     <div className="best-recommendation-page">
//       <h1>Best Recommendation</h1>
//       <p>{recommendation}</p>
//     </div>
//   );
// };

// export default BestRecommendationPage;
// src/pages/BestRecommendationPage.js
import React from 'react';
import { useLocation } from 'react-router-dom';
import { Container, Row, Col, Card } from 'react-bootstrap';

const BestRecommendationPage = () => {
  const location = useLocation();
  const { recommendation } = location.state || { recommendation: 'No recommendation available.' };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={8} className="text-center">
          <Card className="shadow">
            <Card.Body>
              <Card.Title className="mb-4">Best Recommendation</Card.Title>
              <Card.Text>{recommendation}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default BestRecommendationPage;