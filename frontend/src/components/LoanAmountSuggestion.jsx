import React, { useState } from "react";
import { fetchData } from "../api";
import { fieldLabels } from "./fieldLabels";

const LoanAmountSuggestion = () => {
    const [formData, setFormData] = useState({
        income_annum: 100000,
        cibil_score: 750,
        assets: 2000000,
        loan_term: 36,
        no_of_dependents: 2,
        education: 1,
        self_employed: 0,
    });

    const [result, setResult] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: Number(e.target.value) });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetchData("recommend-loan", formData);
        console.log(response);
        setResult(response);
    };

    return (
        <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-700">Loan Amount Suggestion</h2>
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
                    className="w-full bg-green-500 text-white p-2 rounded-md hover:bg-green-600 hover:cursor-pointer"
                >
                    Get Loan Amount
                </button>
            </form>
            {result && (
                <p
                    className={`text-lg font-semibold ${result.error ? "text-red-600" : "text-blue-600"
                        }`}
                >
                    {result.error
                        ? `${result.error}`
                        : `Suggested Loan Amount: ${result.loan_amount}`}
                </p>
            )}
        </div>
    );
};

export default LoanAmountSuggestion;
