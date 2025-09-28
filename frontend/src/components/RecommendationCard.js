// components/RecommendationCard.js
const RecommendationCard = ({ recommendations, onAccept, loading }) => {
  if (!recommendations) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h3 className="text-lg font-semibold mb-3">Recommendations</h3>
      
      <div className="space-y-3">
        <div className="text-sm">
          <strong>Objective Value:</strong> {recommendations.objective.toFixed(1)}
        </div>
        
        <div className="text-sm">
          <strong>Solve Status:</strong> {recommendations.solve_info.status}
        </div>

        {recommendations.allocations.length > 0 && (
          <div>
            <div className="text-sm font-medium mb-2">Allocations:</div>
            <div className="space-y-2">
              {recommendations.allocations.map((allocation, index) => (
                <div key={index} className="text-sm bg-gray-50 p-2 rounded">
                  <div><strong>{allocation.district}:</strong></div>
                  <div>{allocation.count}x {allocation.truck_class}</div>
                  <div>ETA: {allocation.eta_hours}h</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex space-x-2 pt-2">
          <button
            onClick={onAccept}
            disabled={loading}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded transition-colors"
          >
            {loading ? 'Accepting...' : 'Accept'}
          </button>
          <button className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded transition-colors">
            Modify
          </button>
        </div>
      </div>
    </div>
  );
};

export default { RecommendationCard };