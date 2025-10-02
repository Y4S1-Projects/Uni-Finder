
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Row, Col, Button, Card, ListGroup, Alert, Spinner } from 'react-bootstrap';

const RecommendationsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { keyword } = location.state || { keyword: '' }; // Get the selected keyword
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (keyword) {
      // Fetch recommendations based on the selected keyword
      const fetchRecommendations = async () => {
        setLoading(true);
        setError('');
        try {
          const response = await axios.post('http://localhost:5001/recommend', {
            user_input: keyword,
          });
          
          // Ensure response.data is an array
          if (Array.isArray(response.data)) {
            setRecommendations(response.data);
          } else if (response.data && response.data.error) {
            setError(response.data.error);
            setRecommendations([]);
          } else {
            console.warn('Unexpected response format:', response.data);
            setRecommendations([]);
          }
        } catch (error) {
          console.error('Error fetching recommendations:', error);
          setError('Failed to fetch recommendations. Please make sure the server is running.');
          setRecommendations([]);
        } finally {
          setLoading(false);
        }
      };
      fetchRecommendations();
    }
  }, [keyword]);

  const handleShowBestRecommendation = async () => {
    try {
      if (recommendations.length > 0) {
        const response = await axios.post('http://localhost:5001/best_recommendation', {
          user_input: keyword,
          recommendations: recommendations,
        });
        
        // Navigate to the best recommendation page with the API response
        navigate('/best-recommendation', { 
          state: { 
            recommendation: response.data.recommendation || response.data.error || 'No recommendation generated.' 
          } 
        });
      } else {
        navigate('/best-recommendation', { state: { recommendation: 'No recommendations available.' } });
      }
    } catch (error) {
      console.error('Error fetching best recommendation:', error);
      // Fallback to simple recommendation
      const bestRecommendation = recommendations.length > 0
        ? recommendations[0].name + " is the top choice because it has a higher rating and temperature."
        : 'No recommendations available.';
      navigate('/best-recommendation', { state: { recommendation: bestRecommendation } });
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={8} className="text-center">
          <Card className="shadow">
            <Card.Body>
              <Card.Title className="mb-4">Recommendations for "{keyword}"</Card.Title>
              
              {loading && (
                <div className="text-center my-4">
                  <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </Spinner>
                  <p className="mt-2">Fetching recommendations...</p>
                </div>
              )}
              
              {error && (
                <Alert variant="danger" className="mb-4">
                  {error}
                </Alert>
              )}
              
              {!loading && !error && recommendations.length === 0 && (
                <Alert variant="info" className="mb-4">
                  No recommendations found for "{keyword}". Try a different search term.
                </Alert>
              )}
              
              {!loading && recommendations.length > 0 && (
                <>
                  <ListGroup>
                    {recommendations.map((place, index) => (
                      <ListGroup.Item key={index}>
                        <strong>{place.name}</strong> - Rating: {place.rating || 'N/A'}, Temperature: {place.temperature || 'N/A'}°C
                        {place.formatted_address && (
                          <div className="text-muted small">{place.formatted_address}</div>
                        )}
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                  <Button
                    variant="success"
                    size="lg"
                    className="mt-4"
                    onClick={handleShowBestRecommendation}
                  >
                    Show Best Recommendation
                  </Button>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default RecommendationsPage;