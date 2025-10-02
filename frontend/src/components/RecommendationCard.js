import React from 'react';

const RecommendationCard = ({ place }) => {
  return (
    <div className="recommendation-card">
      <h2>{place.name}</h2>
      <p>{place.formatted_address}</p>
      <p>Rating: {place.rating}</p>
      <p>Temperature: {place.temperature}°C</p>
      <p>Final Score: {place.final_score}</p>
    </div>
  );
};

export default RecommendationCard;