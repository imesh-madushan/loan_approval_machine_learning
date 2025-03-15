export const API_BASE_URL = "http://localhost:5000";  // Change to your backend URL

export const fetchData = async (endpoint, data) => {
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        return response.json();
    } catch (error) {
        console.error("Error:", error);
        return { error: "Something went wrong!" };
    }
};
