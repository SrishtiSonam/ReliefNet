import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Activity,
    Brain,
    TrendingUp,
    Truck,
    Plane,
    AlertTriangle,
    MapPin,
    Users,
    Shield,
    ArrowRight,
    Zap,
    Database,
    GitBranch,
    Target,
    Eye
} from 'lucide-react';

const Home = () => {
    const navigate = useNavigate();
    const [activeStep, setActiveStep] = useState(0);
    const [isVisible, setIsVisible] = useState(false);
    const [isTransitioning, setIsTransitioning] = useState(true);

    useEffect(() => {
        setIsVisible(true);
        const interval = setInterval(() => {
            setIsTransitioning(true);
            setActiveStep((prev) => prev + 1);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    // Handle infinite loop reset
    useEffect(() => {
        if (activeStep === 7) {
            setTimeout(() => {
                setIsTransitioning(false);
                setActiveStep(0);
            }, 500);
            setTimeout(() => {
                setIsTransitioning(true);
            }, 550);
        }
    }, [activeStep]);

    const workflowSteps = [
        {
            icon: Database,
            title: 'Data Collection',
            desc: 'Real-time disaster data from across India',
            color: 'from-blue-500 to-cyan-500'
        },
        {
            icon: TrendingUp,
            title: 'ML Forecasting',
            desc: 'ARIMA + GARCH predict demand surges',
            color: 'from-purple-500 to-pink-500'
        },
        {
            icon: Brain,
            title: 'Value Function',
            desc: 'Neural network estimates state values',
            color: 'from-green-500 to-emerald-500'
        },
        {
            icon: GitBranch,
            title: 'Optimization',
            desc: 'OR-Tools finds optimal routes',
            color: 'from-orange-500 to-red-500'
        },
        {
            icon: Eye,
            title: 'Explainability',
            desc: 'SHAP explains AI decisions',
            color: 'from-indigo-500 to-purple-500'
        },
        {
            icon: Target,
            title: 'Allocation',
            desc: 'Resources assigned to districts',
            color: 'from-yellow-500 to-orange-500'
        },
        {
            icon: Truck,
            title: 'Tracking',
            desc: 'Real-time vehicle monitoring',
            color: 'from-teal-500 to-cyan-500'
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
            {/* Navigation Bar */}
            <nav className="bg-white border-b border-gray-200 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Shield className="w-8 h-8 text-blue-600" />
                            <span className="text-2xl font-bold text-gray-900">ReliefNet</span>
                        </div>
                        <button
                            onClick={() => navigate('/login')}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
                        >
                            <Users className="w-4 h-4" />
                            Login
                        </button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
                <div className="max-w-7xl mx-auto px-6 py-20">
                    <div className="text-center space-y-6">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 rounded-full border border-blue-200">
                            <Activity className="w-4 h-4 text-blue-600" />
                            <span className="text-blue-700 text-sm font-medium">Live ML Demonstration System</span>
                        </div>

                        <h1 className="text-5xl md:text-7xl font-bold text-gray-900 leading-tight">
                            ReliefNet
                            <span className="block text-blue-600">
                                AI-Powered Disaster Relief
                            </span>
                        </h1>

                        <p className="text-xl md:text-2xl text-gray-700 max-w-4xl mx-auto leading-relaxed">
                            Stochastic Dynamic Post-Disaster Inventory Allocation Using Trucks and UAVs
                            <span className="block mt-2 text-lg text-gray-600">
                                With Surge Forecasting, Value Function Approximation, Optimization & Explainable AI
                            </span>
                        </p>
                    </div>
                </div>
            </div>

            {/* ML Workflow Timeline - Infinite Sliding Carousel */}
            <div className="max-w-7xl mx-auto px-6 py-20">
                <div className="text-center mb-12">
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">Complete ML Pipeline</h2>
                    <p className="text-gray-600 text-lg">Watch how data flows through our AI system</p>
                </div>

                <div className="relative">
                    {/* Carousel Container */}
                    <div className="overflow-hidden">
                        <div
                            className={`flex ${isTransitioning ? 'transition-transform duration-500 ease-out' : ''}`}
                            style={{ transform: `translateX(-${activeStep * (100 / 3)}%)` }}
                        >
                            {/* Render items + first item again for infinite loop */}
                            {[...workflowSteps, workflowSteps[0]].map((step, index) => {
                                const Icon = step.icon;
                                const displayIndex = index % workflowSteps.length;
                                const isActive = activeStep % workflowSteps.length === displayIndex;

                                return (
                                    <div key={index} className="flex-shrink-0 w-full md:w-1/3 px-4">
                                        <div className={`
                                            relative p-8 rounded-2xl border transition-all duration-500
                                            h-80 flex flex-col items-center justify-center bg-white
                                            ${isActive
                                                ? 'border-blue-400 scale-105 shadow-xl'
                                                : 'border-gray-200 shadow-md'
                                            }
                                        `}>
                                            <div className={`
                                                w-20 h-20 rounded-xl bg-gradient-to-br ${step.color} 
                                                flex items-center justify-center mb-6
                                                ${isActive ? 'animate-pulse' : ''}
                                            `}>
                                                <Icon className="w-10 h-10 text-white" />
                                            </div>

                                            <h3 className="text-2xl font-bold text-gray-900 text-center mb-3">{step.title}</h3>
                                            <p className="text-gray-600 text-center text-base leading-relaxed">{step.desc}</p>

                                            {/* Step Number */}
                                            <div className="absolute top-4 right-4 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                                                <span className="text-blue-600 font-bold text-sm">{displayIndex + 1}</span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Navigation Dots */}
                    <div className="flex justify-center gap-2 mt-8">
                        {workflowSteps.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => {
                                    setIsTransitioning(true);
                                    setActiveStep(index);
                                }}
                                className={`
                                    w-3 h-3 rounded-full transition-all duration-300
                                    ${activeStep % workflowSteps.length === index
                                        ? 'bg-blue-600 w-8'
                                        : 'bg-gray-300 hover:bg-gray-400'
                                    }
                                `}
                            />
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer CTA */}
            <div className="max-w-7xl mx-auto px-6 py-20">
                <div className="rounded-3xl bg-blue-500 p-12 text-center shadow-xl">
                    <div>
                        <AlertTriangle className="w-16 h-16 text-white mx-auto mb-6" />
                        <h2 className="text-4xl font-bold text-white mb-4">
                            Understanding AI for Disaster Relief
                        </h2>
                        <p className="text-xl text-white mb-8 max-w-2xl mx-auto">
                            This is an educational demonstration showing how machine learning, optimization, and explainable AI work together to save lives during disasters across India.
                        </p>
                        <button
                            onClick={() => navigate('/how-ai-works')}
                            className="px-10 py-4 bg-white text-blue-600 rounded-xl font-bold text-lg hover:bg-gray-100 transition-colors inline-flex items-center gap-3"
                        >
                            <Brain className="w-6 h-6" />
                            Learn How It Works
                            <ArrowRight className="w-6 h-6" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
