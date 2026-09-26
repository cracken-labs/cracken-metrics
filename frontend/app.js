document.getElementById('saveBtn').addEventListener('click', async () => {
    const metricNameInput = document.getElementById('metricName');
    const formulaInput = document.getElementById('formulaInput');
    
    const errorBox = document.getElementById('errorBox');
    const placeholderText = document.getElementById('placeholderText');
    const iframe = document.getElementById('chartIframe');
    
    // Очищаем старые ошибки и состояния
    errorBox.style.display = 'none';
    errorBox.innerText = '';

    const metricName = metricNameInput.value.trim();
    const formula = formulaInput.value.trim();

    if (!metricName || !formula) {
        errorBox.innerText = 'Ошибка: Все поля должны быть заполнены!';
        errorBox.style.display = 'block';
        return;
    }

    try {
        // Делаем асинхронный запрос к FastAPI, работающему в Docker
                // Вместо http://localhost:8000/api/convert пишем просто /api/convert
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                formula: formula,
                metric_name: metricName
            })
        });

        const result = await response.json();

        if (!response.ok) {
            // Если бэкенд выкинул 400 (например, ошибка регулярки или синтаксиса)
            throw new Error(result.detail || 'Не удалось обработать формулу');
        }

        // Если всё успешно: прячем текст, отображаем iframe и загружаем ссылку Grafana
        placeholderText.style.display = 'none';
        iframe.style.display = 'block';
        iframe.src = result.render_url;

    } catch (error) {
        // В случае сбоя возвращаем заглушку и выводим ошибку
        iframe.style.display = 'none';
        placeholderText.style.display = 'block';
        errorBox.innerText = error.message;
        errorBox.style.display = 'block';
    }
});
