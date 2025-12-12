import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    TrendingUp,
    Brain,
    Eye,
    Sliders,
    BarChart3,
    GitBranch,
    AlertCircle,
    Info,
    Zap,
    ArrowRight,
    CheckCircle,
    Shield,
    Users,
    Home as HomeIcon
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart, Cell } from 'recharts';

const HowAIWorks = () => {
    const navigate = useNavigate();

    // Interactive ML Experiment State
    const [rainfall, setRainfall] = useState(50);
    const [demand, setDemand] = useState(5000);
    const [stock, setStock] = useState(8000);
    const [trucks, setTrucks] = useState(5);
    const [populationDensity, setPopulationDensity] = useState(5000); // people per sq km
    const [roadAccessibility, setRoadAccessibility] = useState(70); // percentage
    const [distanceToWarehouse, setDistanceToWarehouse] = useState(50); // km
    const [deprivationTime, setDeprivationTime] = useState(24); // hours

    const [allocationResult, setAllocationResult] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [processingStep, setProcessingStep] = useState(0);

    // Animation states for other sections
    const [forecastAnimating, setForecastAnimating] = useState(true);
    const [shapAnimating, setShapAnimating] = useState(true);

    // Calculate allocation based on inputs with animation
    useEffect(() => {
        setIsProcessing(true);
        setProcessingStep(0);

        const steps = [
            { step: 1, delay: 200 },
            { step: 2, delay: 400 },
            { step: 3, delay: 600 },
            { step: 4, delay: 800 },
            { step: 5, delay: 1000 }
        ];

        steps.forEach(({ step, delay }) => {
            setTimeout(() => setProcessingStep(step), delay);
        });

        setTimeout(() => {
            // EDUCATIONAL MOCK ML LOGIC - Enhanced with more features
            // This simulates how ML models make decisions

            // 1. Demand Surge Calculation (ARIMA/GARCH simulation)
            const rainfallFactor = 1 + (rainfall / 100) * 0.5; // More rain = more demand
            const populationFactor = 1 + (populationDensity / 10000) * 0.3; // Higher density = more demand
            const deprivationFactor = 1 + (deprivationTime / 48) * 0.4; // Longer deprivation = more urgent
            const adjustedDemand = Math.round(demand * rainfallFactor * populationFactor * deprivationFactor);

            // 2. VFA Score Calculation (Value Function Approximation)
            const stockRatio = stock / adjustedDemand;
            const accessibilityScore = roadAccessibility / 100;
            const distanceScore = Math.max(0, 1 - (distanceToWarehouse / 200)); // Closer = better
            const vfaScore = Math.min(1,
                stockRatio * 0.4 +
                (trucks / 10) * 0.2 +
                accessibilityScore * 0.2 +
                distanceScore * 0.2
            );

            // 3. Vehicle Selection (Truck vs UAV logic)
            const needUAV = rainfall > 70 || roadAccessibility < 50 || stockRatio < 0.5;
            const trucksNeeded = roadAccessibility > 40 ? Math.min(trucks, Math.ceil(adjustedDemand / 1000)) : 0;
            const uavsNeeded = needUAV ? Math.ceil((adjustedDemand - trucksNeeded * 1000) / 50) : 0;

            // 4. Priority Calculation
            const urgencyScore = (rainfall / 100) * 0.3 + (deprivationTime / 48) * 0.3 + (1 - stockRatio) * 0.4;
            const urgency = urgencyScore > 0.6 ? 'High' : urgencyScore > 0.3 ? 'Medium' : 'Low';

            // 5. Feature Importance (for visualization)
            const featureImpact = {
                rainfall: (rainfall / 100) * 0.25,
                population: (populationDensity / 10000) * 0.2,
                roadAccess: (roadAccessibility / 100) * 0.15,
                distance: -(distanceToWarehouse / 200) * 0.15,
                deprivation: (deprivationTime / 48) * 0.15,
                stock: (stock / 15000) * 0.1
            };

            setAllocationResult({
                adjustedDemand,
                vfaScore: vfaScore.toFixed(2),
                trucksNeeded,
                uavsNeeded,
                urgency,
                urgencyScore: urgencyScore.toFixed(2),
                canMeetDemand: stock >= adjustedDemand,
                featureImpact,
                rainfallFactor: rainfallFactor.toFixed(2),
                populationFactor: populationFactor.toFixed(2),
                deprivationFactor: deprivationFactor.toFixed(2)
            });

            setIsProcessing(false);
        }, 1200);
    }, [rainfall, demand, stock, trucks, populationDensity, roadAccessibility, distanceToWarehouse, deprivationTime]);

    // Enhanced ARIMA + GARCH Forecast Data with realistic patterns
    // 14 days historical + 7 days forecast with disaster events and volatility
    const forecastData = [
        // Historical Period (Days -13 to 0) - showing realistic demand patterns
        { day: 'D-13', actual: 3200, arima: 3180, garch: 3210, confidence_low: 3050, confidence_high: 3350, event: null, isForecast: false },
        { day: 'D-12', actual: 3350, arima: 3320, garch: 3380, confidence_low: 3180, confidence_high: 3520, event: null, isForecast: false },
        { day: 'D-11', actual: 3180, arima: 3200, garch: 3150, confidence_low: 3020, confidence_high: 3380, event: null, isForecast: false },
        { day: 'D-10', actual: 3420, arima: 3450, garch: 3400, confidence_low: 3250, confidence_high: 3650, event: null, isForecast: false },
        { day: 'D-9', actual: 3580, arima: 3600, garch: 3560, confidence_low: 3400, confidence_high: 3800, event: null, isForecast: false },
        { day: 'D-8', actual: 3750, arima: 3720, garch: 3780, confidence_low: 3550, confidence_high: 3950, event: null, isForecast: false },
        { day: 'D-7', actual: 4100, arima: 4050, garch: 4130, confidence_low: 3850, confidence_high: 4350, event: 'Heavy Rain Alert', isForecast: false },
        { day: 'D-6', actual: 4850, arima: 4800, garch: 4900, confidence_low: 4500, confidence_high: 5200, event: null, isForecast: false },
        { day: 'D-5', actual: 5200, arima: 5150, garch: 5250, confidence_low: 4800, confidence_high: 5600, event: null, isForecast: false },
        { day: 'D-4', actual: 5650, arima: 5600, garch: 5700, confidence_low: 5200, confidence_high: 6100, event: 'Cyclone Warning', isForecast: false },
        { day: 'D-3', actual: 6800, arima: 6750, garch: 6850, confidence_low: 6300, confidence_high: 7300, event: null, isForecast: false },
        { day: 'D-2', actual: 7200, arima: 7100, garch: 7250, confidence_low: 6600, confidence_high: 7800, event: null, isForecast: false },
        { day: 'D-1', actual: 6950, arima: 6900, garch: 7000, confidence_low: 6400, confidence_high: 7500, event: null, isForecast: false },
        { day: 'Today', actual: 6500, arima: 6450, garch: 6550, confidence_low: 6000, confidence_high: 7000, event: null, isForecast: false },

        // Forecast Period (Days +1 to +7) - widening confidence intervals
        { day: '+1', actual: null, arima: 6200, garch: 6300, confidence_low: 5600, confidence_high: 6900, event: null, isForecast: true },
        { day: '+2', actual: null, arima: 5850, garch: 6000, confidence_low: 5100, confidence_high: 6800, event: 'Rain Expected', isForecast: true },
        { day: '+3', actual: null, arima: 5500, garch: 5700, confidence_low: 4600, confidence_high: 6800, event: null, isForecast: true },
        { day: '+4', actual: null, arima: 5200, garch: 5450, confidence_low: 4200, confidence_high: 6700, event: null, isForecast: true },
        { day: '+5', actual: null, arima: 4900, garch: 5200, confidence_low: 3800, confidence_high: 6600, event: null, isForecast: true },
        { day: '+6', actual: null, arima: 4650, garch: 5000, confidence_low: 3500, confidence_high: 6500, event: null, isForecast: true },
        { day: '+7', actual: null, arima: 4400, garch: 4800, confidence_low: 3200, confidence_high: 6400, event: null, isForecast: true },
    ];

    // Mock SHAP Values (Feature Importance)
    const shapData = [
        { feature: 'Food Inventory', impact: 0.25, positive: true },
        { feature: 'Rainfall Forecast', impact: 0.18, positive: false },
        { feature: 'Population Density', impact: 0.15, positive: true },
        { feature: 'Road Accessibility', impact: 0.12, positive: true },
        { feature: 'Distance to Warehouse', impact: -0.10, positive: false },
        { feature: 'Truck Availability', impact: 0.09, positive: true },
        { feature: 'Historical Demand', impact: 0.08, positive: true },
        { feature: 'Deprivation Time', impact: -0.07, positive: false },
    ];

    // Surge Index Data
    const surgeData = [
        { district: 'Mumbai', surge: 85, color: '#ef4444' },
        { district: 'Chennai', surge: 72, color: '#f97316' },
        { district: 'Kolkata', surge: 65, color: '#eab308' },
        { district: 'Delhi', surge: 48, color: '#22c55e' },
        { district: 'Bangalore', surge: 35, color: '#22c55e' },
    ];

    // District Priority Table
    const districtPriority = [
        { district: 'Mumbai, Maharashtra', priority: 1, demand: 8500, stock: 6000, trucks: 3, uavs: 5, status: 'Critical' },
        { district: 'Chennai, Tamil Nadu', priority: 2, demand: 6200, stock: 7000, trucks: 2, uavs: 3, status: 'High' },
        { district: 'Kolkata, West Bengal', priority: 3, demand: 5800, stock: 8000, trucks: 2, uavs: 2, status: 'Medium' },
        { district: 'Delhi NCR', priority: 4, demand: 4500, stock: 9000, trucks: 1, uavs: 1, status: 'Low' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
            {/* Navigation Bar */}
            <nav className="bg-white border-b border-gray-200 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-6">
                            <div className="flex items-center gap-2">
                                <Shield className="w-8 h-8 text-blue-600" />
                                <span className="text-2xl font-bold text-gray-900">ReliefNet</span>
                            </div>
                            <button
                                onClick={() => navigate('/')}
                                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
                            >
                                <HomeIcon className="w-4 h-4" />
                                Home
                            </button>
                        </div>
                        <button
                            onClick={() => navigate('/login')}
                            className="px-6 py-2 bg-blue-600 text-black rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
                        >
                            <Users className="w-4 h-4" />
                            Login
                        </button>
                    </div>
                </div>
            </nav>

            <div className="py-12 px-6">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-16">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 rounded-full border border-purple-200 mb-6">
                            <Brain className="w-4 h-4 text-purple-600" />
                            <span className="text-purple-700 text-sm font-medium">Educational ML Demonstration</span>
                        </div>

                        <h1 className="text-5xl font-bold text-gray-900 mb-4">
                            How the <span className="text-blue-600">AI Works</span>
                        </h1>
                        <p className="text-xl text-gray-700 max-w-3xl mx-auto">
                            Understand the machine learning pipeline that powers disaster relief allocation across India
                        </p>
                    </div>

                    {/* Section 1: Forecasting Visualizer */}
                    <div className="mb-16 bg-white/90 backdrop-blur-md rounded-2xl border border-blue-100 shadow-lg p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
                                <TrendingUp className="w-6 h-6 text-black" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">ML Forecasting: ARIMA + GARCH</h2>
                                <p className="text-gray-600">Predicting resource demand 7 days ahead</p>
                            </div>
                        </div>

                        <div className="bg-blue-50/50 rounded-xl p-6 mb-6">
                            <div className="mb-4 flex items-start gap-3 text-sm text-gray-700 bg-blue-100 border border-blue-200 rounded-lg p-4">
                                <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-semibold text-blue-700 mb-1">How it works:</p>
                                    <p><strong>ARIMA</strong> (AutoRegressive Integrated Moving Average) analyzes historical patterns to predict future demand.</p>
                                    <p className="mt-1"><strong>GARCH</strong> (Generalized AutoRegressive Conditional Heteroskedasticity) models volatility to detect demand surges during disasters.</p>
                                    <p className="mt-1">The ensemble combines both models with confidence intervals to provide robust 7-day forecasts for food, water, medicine, and shelter needs.</p>
                                </div>
                            </div>

                            <ResponsiveContainer width="100%" height={400}>
                                <AreaChart data={forecastData}>
                                    <defs>
                                        <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05} />
                                        </linearGradient>
                                        <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#d1d5db" opacity={0.5} />
                                    <XAxis
                                        dataKey="day"
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                        angle={-45}
                                        textAnchor="end"
                                        height={60}
                                    />
                                    <YAxis
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280' }}
                                        label={{ value: 'Demand (kg)', angle: -90, position: 'insideLeft', fill: '#6b7280', style: { fontWeight: 600 } }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#1f2937',
                                            border: '1px solid #374151',
                                            borderRadius: '12px',
                                            padding: '12px',
                                            boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
                                        }}
                                        labelStyle={{ color: '#fff', fontWeight: 'bold', marginBottom: '8px' }}
                                        itemStyle={{ color: '#e5e7eb', fontSize: '13px' }}
                                        content={({ active, payload, label }) => {
                                            if (active && payload && payload.length) {
                                                const data = payload[0].payload;
                                                return (
                                                    <div style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '12px', padding: '12px' }}>
                                                        <p style={{ color: '#fff', fontWeight: 'bold', marginBottom: '8px' }}>{label}</p>
                                                        {data.actual && <p style={{ color: '#10b981', fontSize: '13px' }}>Actual: {data.actual.toLocaleString()} kg</p>}
                                                        <p style={{ color: '#8b5cf6', fontSize: '13px' }}>ARIMA: {data.arima.toLocaleString()} kg</p>
                                                        <p style={{ color: '#ec4899', fontSize: '13px' }}>GARCH: {data.garch.toLocaleString()} kg</p>
                                                        <p style={{ color: '#9ca3af', fontSize: '12px', marginTop: '4px' }}>
                                                            CI: {data.confidence_low.toLocaleString()} - {data.confidence_high.toLocaleString()} kg
                                                        </p>
                                                        {data.event && (
                                                            <p style={{ color: '#fbbf24', fontSize: '12px', marginTop: '8px', fontWeight: 'bold', borderTop: '1px solid #374151', paddingTop: '8px' }}>
                                                                ⚠️ {data.event}
                                                            </p>
                                                        )}
                                                        {data.isForecast && (
                                                            <p style={{ color: '#60a5fa', fontSize: '11px', marginTop: '4px', fontStyle: 'italic' }}>
                                                                📊 Forecast
                                                            </p>
                                                        )}
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
                                    />
                                    <Legend
                                        wrapperStyle={{ paddingTop: '20px' }}
                                        iconType="line"
                                    />

                                    {/* Confidence Interval Area */}
                                    <Area
                                        type="monotone"
                                        dataKey="confidence_high"
                                        stroke="none"
                                        fill="url(#colorConfidence)"
                                        fillOpacity={1}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="confidence_low"
                                        stroke="none"
                                        fill="url(#colorConfidence)"
                                        fillOpacity={1}
                                    />

                                    {/* Actual Demand with Area Fill */}
                                    <Area
                                        type="monotone"
                                        dataKey="actual"
                                        stroke="#10b981"
                                        strokeWidth={3}
                                        fill="url(#colorActual)"
                                        name="Actual Demand"
                                        dot={{ r: 5, fill: '#10b981', strokeWidth: 2, stroke: '#fff' }}
                                        activeDot={{ r: 7 }}
                                    />

                                    {/* ARIMA Forecast */}
                                    <Line
                                        type="monotone"
                                        dataKey="arima"
                                        stroke="#8b5cf6"
                                        strokeWidth={2.5}
                                        name="ARIMA Forecast"
                                        strokeDasharray="5 5"
                                        dot={{ r: 4, fill: '#8b5cf6' }}
                                    />

                                    {/* GARCH Forecast */}
                                    <Line
                                        type="monotone"
                                        dataKey="garch"
                                        stroke="#ec4899"
                                        strokeWidth={2.5}
                                        name="GARCH Forecast"
                                        strokeDasharray="3 3"
                                        dot={{ r: 4, fill: '#ec4899' }}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>

                            {/* Event Markers Legend */}
                            <div className="mt-4 flex flex-wrap gap-4 text-xs">
                                <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-100 border border-yellow-300 rounded-lg">
                                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                                    <span className="text-yellow-800 font-semibold">Event Markers (hover to see)</span>
                                </div>
                                <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-100 border border-purple-300 rounded-lg">
                                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                                    <span className="text-purple-800 font-semibold">Confidence Interval (uncertainty range)</span>
                                </div>
                                <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-100 border border-blue-300 rounded-lg">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                    <span className="text-blue-800 font-semibold">Forecast widens over time (more uncertainty)</span>
                                </div>
                            </div>
                        </div>

                        {/* Surge Index */}
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                Surge Index by District
                                <span className="text-xs text-gray-500 font-normal">(Live ML Predictions)</span>
                            </h3>
                            <div className="space-y-3">
                                {surgeData.map((item, idx) => (
                                    <div key={idx} className="flex items-center gap-4">
                                        <span className="text-gray-700 w-32 font-medium">{item.district}</span>
                                        <div className="flex-1 bg-gray-700/30 rounded-full h-8 overflow-hidden relative">
                                            <div
                                                className="h-full flex items-center justify-end px-3 text-black text-sm font-semibold transition-all duration-1000 animate-pulse"
                                                style={{
                                                    width: `${item.surge}%`,
                                                    backgroundColor: item.color,
                                                    animationDuration: `${2 + idx * 0.2}s`
                                                }}
                                            >
                                                {item.surge}%
                                            </div>
                                            {/* Animated shimmer effect */}
                                            <div
                                                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"
                                                style={{
                                                    animationDelay: `${idx * 0.3}s`,
                                                    width: `${item.surge}%`
                                                }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Data Flow Visualization */}
                            <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                                <div className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 bg-blue-500 rounded-full animate-ping"></div>
                                        <span className="text-gray-700 font-semibold">Historical Data</span>
                                    </div>
                                    <ArrowRight className="w-4 h-4 text-gray-400 animate-pulse" />
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 bg-purple-500 rounded-full animate-ping" style={{ animationDelay: '0.3s' }}></div>
                                        <span className="text-gray-700 font-semibold">ARIMA Model</span>
                                    </div>
                                    <ArrowRight className="w-4 h-4 text-gray-400 animate-pulse" style={{ animationDelay: '0.3s' }} />
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 bg-pink-500 rounded-full animate-ping" style={{ animationDelay: '0.6s' }}></div>
                                        <span className="text-gray-700 font-semibold">GARCH Model</span>
                                    </div>
                                    <ArrowRight className="w-4 h-4 text-gray-400 animate-pulse" style={{ animationDelay: '0.6s' }} />
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 bg-green-500 rounded-full animate-ping" style={{ animationDelay: '0.9s' }}></div>
                                        <span className="text-gray-700 font-semibold">Forecast</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Section 2: Allocation Engine Demo */}
                    <div className="mb-16 bg-white/90 backdrop-blur-md rounded-2xl border border-blue-100 shadow-lg p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-600 to-red-600 flex items-center justify-center">
                                <GitBranch className="w-6 h-6 text-black" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Allocation Engine: OR-Tools Optimization</h2>
                                <p className="text-gray-600">How trucks and UAVs are assigned to districts</p>
                            </div>
                        </div>

                        <div className="bg-blue-50/50 rounded-xl p-6 mb-6">
                            <div className="mb-4 flex items-start gap-3 text-sm text-gray-700 bg-orange-100 border border-orange-200 rounded-lg p-4">
                                <Info className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-semibold text-orange-700 mb-1">Optimization Logic:</p>
                                    <p>1. <strong>Priority Scoring:</strong> Districts ranked by urgency, accessibility, and deprivation time</p>
                                    <p>2. <strong>Capacity Constraints:</strong> Trucks carry 5000kg, UAVs carry 50kg</p>
                                    <p>3. <strong>Route Optimization:</strong> OR-Tools minimizes total distance while maximizing coverage</p>
                                    <p>4. <strong>UAV Selection:</strong> Used for remote areas, road blockages, or medical emergencies</p>
                                </div>
                            </div>

                            {/* Optimization Process Visualization */}
                            <div className="mb-4 p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border border-orange-200">
                                <div className="flex items-center gap-2 mb-3">
                                    <GitBranch className="w-4 h-4 text-orange-600 animate-pulse" />
                                    <span className="text-sm font-semibold text-orange-700">OR-Tools Processing</span>
                                </div>
                                <div className="flex items-center justify-between text-xs">
                                    <div className="flex items-center gap-1">
                                        <div className="w-2 h-2 bg-orange-500 rounded-full animate-ping"></div>
                                        <span className="text-gray-600">Input Constraints</span>
                                    </div>
                                    <ArrowRight className="w-3 h-3 text-gray-400" />
                                    <div className="flex items-center gap-1">
                                        <div className="w-2 h-2 bg-red-500 rounded-full animate-ping" style={{ animationDelay: '0.3s' }}></div>
                                        <span className="text-gray-600">Linear Programming</span>
                                    </div>
                                    <ArrowRight className="w-3 h-3 text-gray-400" />
                                    <div className="flex items-center gap-1">
                                        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-ping" style={{ animationDelay: '0.6s' }}></div>
                                        <span className="text-gray-600">Vehicle Assignment</span>
                                    </div>
                                    <ArrowRight className="w-3 h-3 text-gray-400" />
                                    <div className="flex items-center gap-1">
                                        <div className="w-2 h-2 bg-green-500 rounded-full animate-ping" style={{ animationDelay: '0.9s' }}></div>
                                        <span className="text-gray-600">Optimal Routes</span>
                                    </div>
                                </div>
                            </div>

                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-gray-700">
                                            <th className="text-left py-3 px-4 text-gray-900 font-semibold">District</th>
                                            <th className="text-right py-3 px-4 text-gray-900 font-semibold">Priority</th>
                                            <th className="text-right py-3 px-4 text-gray-900 font-semibold">Demand (kg)</th>
                                            <th className="text-right py-3 px-4 text-gray-900 font-semibold">Stock (kg)</th>
                                            <th className="text-right py-3 px-4 text-gray-900 font-semibold">Trucks</th>
                                            <th className="text-right py-3 px-4 text-gray-900 font-semibold">UAVs</th>
                                            <th className="text-center py-3 px-4 text-gray-900 font-semibold">Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {districtPriority.map((row, idx) => (
                                            <tr key={idx} className="border-b border-gray-200 hover:bg-blue-50 transition-all duration-300 hover:shadow-md">
                                                <td className="py-3 px-4 text-gray-900">{row.district}</td>
                                                <td className="py-3 px-4 text-right">
                                                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 font-bold animate-pulse" style={{ animationDuration: `${2 + idx * 0.3}s` }}>
                                                        {row.priority}
                                                    </span>
                                                </td>
                                                <td className="py-3 px-4 text-right text-gray-700">{row.demand.toLocaleString()}</td>
                                                <td className="py-3 px-4 text-right text-gray-700">{row.stock.toLocaleString()}</td>
                                                <td className="py-3 px-4 text-right text-gray-700">{row.trucks}</td>
                                                <td className="py-3 px-4 text-right text-gray-700">{row.uavs}</td>
                                                <td className="py-3 px-4 text-center">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-semibold animate-pulse ${row.status === 'Critical' ? 'bg-red-500/20 text-red-400' :
                                                        row.status === 'High' ? 'bg-orange-500/20 text-orange-400' :
                                                            row.status === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                                                'bg-green-500/20 text-green-400'
                                                        }`} style={{ animationDuration: `${1.5 + idx * 0.2}s` }}>
                                                        {row.status}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    {/* Section 3: Explainable AI */}
                    <div className="mb-16 bg-white/90 backdrop-blur-md rounded-2xl border border-blue-100 shadow-lg p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-600 to-emerald-600 flex items-center justify-center">
                                <Eye className="w-6 h-6 text-black" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Explainable AI: SHAP Values</h2>
                                <p className="text-gray-600">Why did the model make this decision?</p>
                            </div>
                        </div>

                        <div className="bg-blue-50/50 rounded-xl p-6 mb-6">
                            <div className="mb-4 flex items-start gap-3 text-sm text-gray-700 bg-green-100 border border-green-200 rounded-lg p-4">
                                <Info className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-semibold text-green-700 mb-1">SHAP Explanation:</p>
                                    <p><strong>SHAP</strong> (SHapley Additive exPlanations) shows how much each feature contributed to the allocation decision.</p>
                                    <p className="mt-1">Positive values (green) increase allocation priority. Negative values (red) decrease it.</p>
                                    <p className="mt-1">This makes AI decisions transparent and trustworthy for disaster management officials.</p>
                                </div>
                            </div>

                            {/* Behind-the-scenes processing visualization */}
                            <div className="mb-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                                <div className="flex items-center gap-2 mb-3">
                                    <Brain className="w-4 h-4 text-green-600 animate-pulse" />
                                    <span className="text-sm font-semibold text-green-700">ML Processing Pipeline</span>
                                </div>
                                <div className="grid grid-cols-4 gap-2 text-xs">
                                    <div className="flex flex-col items-center p-2 bg-white rounded border border-green-200">
                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce mb-1"></div>
                                        <span className="text-gray-600 text-center">Feature Extraction</span>
                                    </div>
                                    <div className="flex flex-col items-center p-2 bg-white rounded border border-green-200">
                                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce mb-1" style={{ animationDelay: '0.2s' }}></div>
                                        <span className="text-gray-600 text-center">SHAP Calculation</span>
                                    </div>
                                    <div className="flex flex-col items-center p-2 bg-white rounded border border-green-200">
                                        <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce mb-1" style={{ animationDelay: '0.4s' }}></div>
                                        <span className="text-gray-600 text-center">Impact Scoring</span>
                                    </div>
                                    <div className="flex flex-col items-center p-2 bg-white rounded border border-green-200">
                                        <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce mb-1" style={{ animationDelay: '0.6s' }}></div>
                                        <span className="text-gray-600 text-center">Explanation Gen</span>
                                    </div>
                                </div>
                            </div>

                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={shapData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                    <XAxis type="number" stroke="#9ca3af" label={{ value: 'SHAP Impact', position: 'insideBottom', offset: -5, fill: '#9ca3af' }} />
                                    <YAxis type="category" dataKey="feature" stroke="#9ca3af" width={150} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                                        labelStyle={{ color: '#fff' }}
                                    />
                                    <Bar dataKey="impact" fill="#8b5cf6">
                                        {shapData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.impact > 0 ? '#10b981' : '#ef4444'} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>

                            <div className="mt-6 p-4 bg-blue-100 border border-blue-200 rounded-lg">
                                <p className="text-sm text-gray-700">
                                    <strong className="text-blue-700">Natural Language Explanation:</strong> The model prioritized this district because
                                    <strong className="text-green-600"> Food Inventory is high (+0.25)</strong> and
                                    <strong className="text-green-600"> Road Accessibility is good (+0.12)</strong>, but
                                    <strong className="text-red-600"> Rainfall Forecast is severe (-0.18)</strong> and
                                    <strong className="text-red-600"> Distance to Warehouse is far (-0.10)</strong>.
                                    Overall, the positive factors outweigh negatives, making this a high-priority allocation.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Section 4: Interactive ML Experiment */}
                    <div className="mb-16 bg-white/90 backdrop-blur-md rounded-2xl border border-blue-100 shadow-lg p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center animate-pulse">
                                <Sliders className="w-6 h-6 text-black" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Interactive ML Experiment</h2>
                                <p className="text-gray-700">Change inputs and see how allocation updates instantly</p>
                            </div>
                        </div>

                        <div className="grid md:grid-cols-2 gap-8">
                            {/* Input Controls */}
                            <div className="space-y-6">
                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Rainfall Forecast (mm)</span>
                                        <span className="text-2xl text-blue-600">{rainfall}mm</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        value={rainfall}
                                        onChange={(e) => setRainfall(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Higher rainfall increases demand surge</p>
                                </div>

                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Base Demand (kg)</span>
                                        <span className="text-2xl text-purple-600">{demand.toLocaleString()}</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="1000"
                                        max="10000"
                                        step="500"
                                        value={demand}
                                        onChange={(e) => setDemand(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Predicted resource need for district</p>
                                </div>

                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Warehouse Stock (kg)</span>
                                        <span className="text-2xl text-green-600">{stock.toLocaleString()}</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="15000"
                                        step="500"
                                        value={stock}
                                        onChange={(e) => setStock(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Available inventory at warehouse</p>
                                </div>

                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Available Trucks</span>
                                        <span className="text-2xl text-orange-600">{trucks}</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="10"
                                        value={trucks}
                                        onChange={(e) => setTrucks(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Trucks available for deployment</p>
                                </div>

                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Population Density (per km²)</span>
                                        <span className="text-2xl text-pink-600">{populationDensity.toLocaleString()}</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="1000"
                                        max="10000"
                                        step="500"
                                        value={populationDensity}
                                        onChange={(e) => setPopulationDensity(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Higher density increases resource needs</p>
                                </div>

                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Road Accessibility (%)</span>
                                        <span className="text-2xl text-teal-600">{roadAccessibility}%</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        value={roadAccessibility}
                                        onChange={(e) => setRoadAccessibility(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Low accessibility triggers UAV deployment</p>
                                </div>

                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Distance to Warehouse (km)</span>
                                        <span className="text-2xl text-indigo-600">{distanceToWarehouse}km</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="10"
                                        max="200"
                                        step="10"
                                        value={distanceToWarehouse}
                                        onChange={(e) => setDistanceToWarehouse(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Greater distance reduces VFA score</p>
                                </div>

                                <div>
                                    <label className="flex items-center justify-between text-gray-900 font-semibold mb-2">
                                        <span>Deprivation Time (hours)</span>
                                        <span className="text-2xl text-red-600">{deprivationTime}h</span>
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="72"
                                        step="6"
                                        value={deprivationTime}
                                        onChange={(e) => setDeprivationTime(Number(e.target.value))}
                                        className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <p className="text-sm text-gray-600 mt-1">Longer deprivation increases urgency</p>
                                </div>
                            </div>

                            {/* Results */}
                            <div className="bg-blue-50/50 rounded-xl p-6 border border-blue-100">
                                <div className="flex items-center gap-2 mb-6">
                                    <Zap className="w-5 h-5 text-yellow-600" />
                                    <h3 className="text-xl font-bold text-gray-900">Allocation Result</h3>
                                </div>

                                {/* Processing Animation */}
                                {isProcessing && (
                                    <div className="mb-6 space-y-2">
                                        <div className="flex items-center gap-3 text-sm">
                                            <div className={`w-2 h-2 rounded-full ${processingStep >= 1 ? 'bg-blue-500 animate-pulse' : 'bg-gray-300'}`}></div>
                                            <span className={processingStep >= 1 ? 'text-blue-600 font-semibold' : 'text-gray-500'}>Calculating demand surge...</span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <div className={`w-2 h-2 rounded-full ${processingStep >= 2 ? 'bg-purple-500 animate-pulse' : 'bg-gray-300'}`}></div>
                                            <span className={processingStep >= 2 ? 'text-purple-600 font-semibold' : 'text-gray-500'}>Computing VFA score...</span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <div className={`w-2 h-2 rounded-full ${processingStep >= 3 ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></div>
                                            <span className={processingStep >= 3 ? 'text-green-600 font-semibold' : 'text-gray-500'}>Selecting vehicles...</span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <div className={`w-2 h-2 rounded-full ${processingStep >= 4 ? 'bg-orange-500 animate-pulse' : 'bg-gray-300'}`}></div>
                                            <span className={processingStep >= 4 ? 'text-orange-600 font-semibold' : 'text-gray-500'}>Calculating priority...</span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <div className={`w-2 h-2 rounded-full ${processingStep >= 5 ? 'bg-pink-500 animate-pulse' : 'bg-gray-300'}`}></div>
                                            <span className={processingStep >= 5 ? 'text-pink-600 font-semibold' : 'text-gray-500'}>Generating explanation...</span>
                                        </div>
                                    </div>
                                )}

                                {allocationResult && (
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-center p-4 bg-blue-100 rounded-lg border border-blue-200">
                                            <span className="text-gray-700">Adjusted Demand</span>
                                            <span className="text-2xl font-bold text-blue-400">{allocationResult.adjustedDemand.toLocaleString()} kg</span>
                                        </div>

                                        <div className="flex justify-between items-center p-4 bg-purple-100 rounded-lg border border-purple-200">
                                            <span className="text-gray-700">VFA Score</span>
                                            <span className="text-2xl font-bold text-purple-400">{allocationResult.vfaScore}</span>
                                        </div>

                                        <div className="flex justify-between items-center p-4 bg-green-100 rounded-lg border border-green-200">
                                            <span className="text-gray-700">Trucks Needed</span>
                                            <span className="text-2xl font-bold text-green-400">{allocationResult.trucksNeeded}</span>
                                        </div>

                                        <div className="flex justify-between items-center p-4 bg-cyan-100 rounded-lg border border-cyan-200">
                                            <span className="text-gray-700">UAVs Needed</span>
                                            <span className="text-2xl font-bold text-cyan-400">{allocationResult.uavsNeeded}</span>
                                        </div>

                                        <div className="flex justify-between items-center p-4 bg-orange-100 rounded-lg border border-orange-200">
                                            <span className="text-gray-700">Urgency Level</span>
                                            <span className={`text-2xl font-bold ${allocationResult.urgency === 'High' ? 'text-red-400' :
                                                allocationResult.urgency === 'Medium' ? 'text-yellow-400' :
                                                    'text-green-400'
                                                }`}>
                                                {allocationResult.urgency}
                                            </span>
                                        </div>

                                        <div className={`flex items-center gap-3 p-4 rounded-lg border ${allocationResult.canMeetDemand
                                            ? 'bg-green-100 border-green-200'
                                            : 'bg-red-100 border-red-200'
                                            }`}>
                                            {allocationResult.canMeetDemand ? (
                                                <>
                                                    <CheckCircle className="w-6 h-6 text-green-400" />
                                                    <span className="text-green-700 font-semibold">Can meet demand with current stock</span>
                                                </>
                                            ) : (
                                                <>
                                                    <AlertCircle className="w-6 h-6 text-red-400" />
                                                    <span className="text-red-700 font-semibold">Insufficient stock - emergency resupply needed</span>
                                                </>
                                            )}
                                        </div>

                                        {/* Feature Impact Visualization */}
                                        <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                                            <h4 className="text-sm font-bold text-gray-900 mb-3">Feature Impact Analysis</h4>
                                            <div className="space-y-2">
                                                {Object.entries(allocationResult.featureImpact).map(([key, value]) => (
                                                    <div key={key} className="flex items-center gap-2">
                                                        <span className="text-xs text-gray-600 w-24 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                                                        <div className="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
                                                            <div
                                                                className={`h-full flex items-center justify-end px-2 text-xs font-semibold text-white transition-all duration-500 ${value > 0 ? 'bg-green-500' : 'bg-red-500'
                                                                    }`}
                                                                style={{
                                                                    width: `${Math.abs(value) * 100}%`,
                                                                    marginLeft: value < 0 ? 'auto' : '0'
                                                                }}
                                                            >
                                                                {(value * 100).toFixed(0)}%
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="mt-6 p-4 bg-gray-100 rounded-lg border border-gray-200">
                                            <p className="text-sm text-gray-700 leading-relaxed">
                                                <strong className="text-gray-900">Behind the Scenes:</strong> Demand multiplied by rainfall factor ({allocationResult.rainfallFactor}×), population factor ({allocationResult.populationFactor}×), and deprivation factor ({allocationResult.deprivationFactor}×).
                                                VFA score combines stock ratio, truck availability, road accessibility ({roadAccessibility}%), and distance ({distanceToWarehouse}km).
                                                {allocationResult.uavsNeeded > 0 && ' UAVs deployed due to high rainfall, poor road access, or low stock ratio.'}
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Key Takeaways */}
                    <div className="bg-blue-500 rounded-2xl p-8 text-center shadow-lg">
                        <h2 className="text-3xl font-bold text-black mb-4">Key Takeaways</h2>
                        <div className="grid md:grid-cols-3 gap-6 mt-8">
                            <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6">
                                <TrendingUp className="w-10 h-10 text-black mx-auto mb-3" />
                                <h3 className="text-xl font-bold text-black mb-2">Forecasting</h3>
                                <p className="text-black">ARIMA + GARCH predict demand 7 days ahead with confidence intervals</p>
                            </div>
                            <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6">
                                <GitBranch className="w-10 h-10 text-black mx-auto mb-3" />
                                <h3 className="text-xl font-bold text-black mb-2">Optimization</h3>
                                <p className="text-black">OR-Tools assigns vehicles to minimize distance and maximize coverage</p>
                            </div>
                            <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6">
                                <Eye className="w-10 h-10 text-black mx-auto mb-3" />
                                <h3 className="text-xl font-bold text-black mb-2">Explainability</h3>
                                <p className="text-black">SHAP values make every AI decision transparent and trustworthy</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HowAIWorks;
