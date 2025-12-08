// Функція для виконання запитів
async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = {
        "Content-Type": "application/json"
    };
    
    // Якщо ми залогінені, можна передавати токен (якщо додамо JWT), 
    // але поки Django використовує сесії або Basic Auth.
    // Для простоти курсової, дані про юзера будемо брати з localStorage і передавати явно в body,
    // або налаштуємо Basic Auth у заголовках, якщо потрібно.

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