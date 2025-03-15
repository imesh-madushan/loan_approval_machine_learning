import React, { useState } from "react";
import { fetchData } from "../api";
import { fieldLabels } from "./fieldLabels";

const FraudDetection = () => {
    const [formData, setFormData] = useState({
        income_annum: 10000000,
        loan_amount: 50000,
        cibil_score: 600,
        assets: 200000
    });

    const [fraudResult, setFraudResult] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: Number(e.target.value) });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetchData("check-fraud", formData);
        console.log(response);
        setFraudResult(response);
    };

    return (
        <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-700">Fraud Detection</h2>
            <form onSubmit={handleSubmit} className="space-y-3">
                            {fieldLabels.filter((({ name }) => name in formData)).map(({ name, label, type, options }) => (
                                <div key={name} className="flex flex-col">
                                    <label className="text-gray-600">{label}</label>
            
                                    {/* Render input field based on type */}
                                    {type === "number" ? (
                                        <input
                                            type="number"
                                            name={name}
                                            value={formData[name]}
                                            onChange={handleChange}
                                            className="border p-2 rounded-md"
                                            required
                                        />
                                    ) : type === "radiol" && options ? (
                                        <div className="flex space-x-4">
                                            {options.map((option, index) => (
                                                <label key={index} className="flex items-center space-x-2">
                                                    <input
                                                        type="radio"
                                                        name={name}
                                                        value={index} // Store index (0/1)
                                                        checked={formData[name] === index}
                                                        onChange={handleChange}
                                                    />
                                                    <span>{option}</span>
                                                </label>
                                            ))}
                                        </div>
                                    ) : null}
                                </div>
                            ))}
                <button
                    type="submit"
                    className="w-full bg-red-500 text-white p-2 rounded-md hover:bg-red-600 hover:cursor-pointer"
                >
                    Check Fraud
                </button>
            </form>
            {fraudResult && (
                <p className={`text-lg font-semibold ${fraudResult.fraud ? "text-red-600" : "text-green-600"}`}>
                    Fraud Detected: {fraudResult.fraud ? "❌ Yes" : "✅ No"}
                </p>
            )}
        </div>
    );
};

export default FraudDetection;
