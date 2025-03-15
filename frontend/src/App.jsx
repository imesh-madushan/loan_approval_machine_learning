import React, { useState } from "react";
import LoanApprovalCheck from "./components/LoanApprovalCheck";
import LoanAmountSuggestion from "./components/LoanAmountSuggestion";
import InterestRatePrediction from "./components/InterestRatePrediction";
import FraudDetection from "./components/FraudDetection";

const App = () => {
    const [selectedFeature, setSelectedFeature] = useState(null);

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center p-5">
            <h1 className="text-3xl font-bold mb-6">Loan Prediction System</h1>

            {!selectedFeature ? (
                <div className="grid grid-cols-2 gap-6">
                    {[
                        { name: "Loan Approval Check", component: "loanApproval" },
                        { name: "Loan Amount Suggestion", component: "loanAmount" },
                        { name: "Interest Rate Prediction", component: "interestRate" },
                        { name: "Fraud Detection", component: "fraudDetection" },
                    ].map((item, index) => (
                        <button
                            key={index}
                            className="p-6 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-all hover:cursor-pointer"
                            onClick={() => setSelectedFeature(item.component)}
                        >
                            {item.name}
                        </button>
                    ))}
                </div>
            ) : (
                <div className="w-full max-w-md bg-white p-6 shadow-md rounded-md mt-6">
                    <button
                        className="mb-4 bg-blue-500 hover:cursor-pointer text-white px-3 py-1 rounded-md hover:bg-blue-600"
                        onClick={() => setSelectedFeature(null)}
                    >
                        ← Back
                    </button>

                    {selectedFeature === "loanApproval" && <LoanApprovalCheck />}
                    {selectedFeature === "loanAmount" && <LoanAmountSuggestion />}
                    {selectedFeature === "interestRate" && <InterestRatePrediction />}
                    {selectedFeature === "fraudDetection" && <FraudDetection />}
                </div>
            )}
        </div>
    );
};

export default App;
