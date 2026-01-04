async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = {
        "Content-Type": "application/json"
    };

    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "API Error");
        }
        return await response.json();
    } catch (error) {
        console.error("API call failed:", error);
        alert("Помилка: " + error.message);
        return null;
    }
}