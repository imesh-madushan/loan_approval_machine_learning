import React, { useState } from "react";
import { fetchData } from "../api";
import { fieldLabels } from "./fieldLabels";

const LoanApprovalCheck = () => {
    const [formData, setFormData] = useState({
        no_of_dependents: 1,
        education: 0,
        self_employed: 0,
        income_annum: 6000000,
        loan_amount: 4000000,
        loan_term: 12,
        cibil_score: 721,
        assets: 40000000
    });

    const [result, setResult] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: Number(e.target.value) });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetchData("check-approval", formData);
        console.log(response);
        setResult(response);
    };

    return (
        <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-700">Loan Approval Check</h2>
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

                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded-md">
                    Check Approval
                </button>
            </form>

            {result && (
                <p className={`text-lg font-semibold ${result.approved ? (result.fraud ? "text-yellow-600" : "text-green-600") : "text-red-600"}`}>
                    {result.approved ? (result.fraud ? "⚠️ Fraud Detected" : "Loan Approved: ✅ Yes") : "Loan Approved: ❌ No"}
                </p>
            )}
        </div>
    );
};

export default LoanApprovalCheck;
