
// import React, { useState } from 'react';
// import { useNavigate } from 'react-router-dom';

// const KeywordsPage = () => {
//   const navigate = useNavigate();
//   const [selectedKeyword, setSelectedKeyword] = useState('');

//   // List of keywords
//   const keywords = [
//     'hiking',
//     'beach',
//     'bicycling',
//     'historical',
//     'wildlife',
//     'bird watching',
//   ];

//   const handleKeywordSelect = (keyword) => {
//     setSelectedKeyword(keyword);
//   };

//   const handleSubmit = () => {
//     if (selectedKeyword) {
//       // Navigate to the recommendations page with the selected keyword
//       navigate('/recommendations', { state: { keyword: selectedKeyword } });
//     } else {
//       alert('Please select a keyword.');
//     }
//   };

//   return (
//     <div className="keywords-page">
//       <h1>Select Your Preferred Activity</h1>
//       <div className="keywords-list">
//         {keywords.map((keyword, index) => (
//           <button
//             key={index}
//             className={selectedKeyword === keyword ? 'selected' : ''}
//             onClick={() => handleKeywordSelect(keyword)}
//           >
//             {keyword}
//           </button>
//         ))}
//       </div>
//       <button onClick={handleSubmit}>Get Recommendations</button>
//     </div>
//   );
// };

// export default KeywordsPage;
// src/pages/KeywordsPage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Row, Col, Button, Card } from 'react-bootstrap';

const KeywordsPage = () => {
  const navigate = useNavigate();
  const [selectedKeyword, setSelectedKeyword] = useState('');

  // List of keywords
  const keywords = [
    'hiking',
    'beach',
    'bicycling',
    'historical',
    'wildlife',
    'bird watching',
    "bbbbbb",
  ];

  const handleKeywordSelect = (keyword) => {
    setSelectedKeyword(keyword);
  };

  const handleSubmit = () => {
    if (selectedKeyword) {
      // Navigate to the recommendations page with the selected keyword
      navigate('/recommendations', { state: { keyword: selectedKeyword } });
    } else {
      alert('Please select a keyword.');
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={8} className="text-center">
          <Card className="shadow">
            <Card.Body style={{ paddingTop: '2rem' }}>
              <Card.Title className="mb-4" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#333' }}>
                Select Your Preferred Activity
              </Card.Title>
              <Row className="mb-4">
                {keywords.map((keyword, index) => (
                  <Col key={index} xs={6} sm={4} className="mb-3">
                    <Button
                      variant={selectedKeyword === keyword ? 'primary' : 'outline-primary'}
                      className="w-100"
                      onClick={() => handleKeywordSelect(keyword)}
                    >
                      {keyword}
                    </Button>
                  </Col>
                ))}
              </Row>
              <Button
                variant="success"
                size="lg"
                onClick={handleSubmit}
                disabled={!selectedKeyword}
              >
                Get Recommendations
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default KeywordsPage;
