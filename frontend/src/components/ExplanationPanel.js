// components/ExplanationPanel.js
const ExplanationPanel = ({ explanation }) => {
  if (!explanation) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h3 className="text-lg font-semibold mb-3">AI Explanation</h3>
      
      <div className="space-y-3">
        <div className="text-sm">
          <strong>Model:</strong> {explanation.model}
        </div>
        
        <div>
          <div className="text-sm font-medium mb-2">Key Factors:</div>
          <div className="space-y-1">
            {explanation.top_features?.map((feature, index) => (
              <div key={index} className="flex items-center">
                <div className="text-sm flex-1">{feature.name}:</div>
                <div className="flex-1">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${feature.score * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-xs text-gray-600 ml-2">
                  {(feature.score * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default { ExplanationPanel };