import React, { useState } from "react";
import { fetchData } from "../api";
import { fieldLabels } from "./fieldLabels";

const InterestRatePrediction = () => {
    const [formData, setFormData] = useState({
        loan_amount: 20000000,
        income_annum: 800000,
    });

    const [interestRate, setInterestRate] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: Number(e.target.value) });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetchData("interest-rate", formData);
        setInterestRate(response);
    };

    return (
        <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-700">Personalized Interest Rate</h2>
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
                    className="w-full bg-purple-500 text-white p-2 rounded-md hover:bg-purple-600 hover:cursor-pointer"
                >
                    Get Interest Rate
                </button>
            </form>
            {interestRate && (
                <p className="text-lg font-semibold text-blue-600">
                    Interest Rate: {interestRate.interest_rate.toFixed(2)}%
                </p>
            )}
        </div>
    );
};

export default InterestRatePrediction;
