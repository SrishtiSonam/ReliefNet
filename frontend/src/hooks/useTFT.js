import { useState, useEffect } from 'react';

/**
 * Custom hook for fetching TFT forecast data
 */
export const useTFTForecast = (district, forecastHorizon = 30) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchForecast = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch('http://localhost:8000/api/tft/forecast', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ district, forecast_horizon: forecastHorizon })
                });

                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        if (district) {
            fetchForecast();
        }
    }, [district, forecastHorizon]);

    return { data, loading, error };
};

/**
 * Custom hook for fetching TFT attention weights
 */
export const useTFTAttention = (district) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAttention = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch(`http://localhost:8000/api/tft/attention?district=${district}`);
                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        if (district) {
            fetchAttention();
        }
    }, [district]);

    return { data, loading, error };
};

/**
 * Custom hook for fetching TFT vs ARIMA comparison
 */
export const useTFTComparison = (district) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchComparison = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch(`http://localhost:8000/api/tft/compare?district=${district}`);
                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        if (district) {
            fetchComparison();
        }
    }, [district]);

    return { data, loading, error };
};
