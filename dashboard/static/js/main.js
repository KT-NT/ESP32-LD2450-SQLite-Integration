document.addEventListener('DOMContentLoaded', function() {
    let lastTimestamp = 0;

    // Переключение разделов "Реальное время" и "История"
    document.getElementById('showLive').addEventListener('click', function() {
        document.getElementById('liveSection').style.display = 'block';
        document.getElementById('historySection').style.display = 'none';
    });
    document.getElementById('showHistory').addEventListener('click', function() {
        document.getElementById('liveSection').style.display = 'none';
        document.getElementById('historySection').style.display = 'block';
    });

    // Инициализация графика для реального времени
    const liveCtx = document.getElementById('liveChart').getContext('2d');
    const liveChart = new Chart(liveCtx, {
        type: 'line',
        data: { datasets: [] },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: { unit: 'second' },
                    title: { display: true, text: 'Время' }
                },
                y: {
                    title: { display: true, text: 'Скорость' }
                }
            }
        }
    });

    // Периодическая загрузка новых данных для реального времени
    setInterval(function() {
        fetch('/api/live?since=' + lastTimestamp)
            .then(response => response.json())
            .then(data => {
                data.forEach(dataset => {
                    let existing = liveChart.data.datasets.find(d => d.label === dataset.label);
                    if (existing) {
                        existing.data.push(...dataset.data);
                    } else {
                        // Новая серия данных
                        liveChart.data.datasets.push({
                            label: dataset.label,
                            data: dataset.data,
                            borderColor: dataset.borderColor,
                            fill: false
                        });
                    }
                    // Обновляем последний timestamp
                    dataset.data.forEach(pt => {
                        if (pt.x > lastTimestamp) {
                            lastTimestamp = pt.x;
                        }
                    });
                });
                liveChart.update();
            });
    }, 2000); // обновление каждые 2 секунды

    // Инициализация графика для исторического режима
    const histCtx = document.getElementById('historyChart').getContext('2d');
    const historyChart = new Chart(histCtx, {
        type: 'line',
        data: { datasets: [] },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: { unit: 'second' },
                    title: { display: true, text: 'Время' }
                },
                y: {
                    title: { display: true, text: 'Скорость' }
                }
            }
        }
    });

    // Загрузка данных при выборе интервала
    document.getElementById('loadHistory').addEventListener('click', function() {
        const start = document.getElementById('startTime').value;
        const end = document.getElementById('endTime').value;
        if (!start || !end) {
            alert('Укажите начальное и конечное время');
            return;
        }
        fetch(`/api/history?start=${start}&end=${end}`)
            .then(response => response.json())
            .then(data => {
                // Очищаем старые данные и добавляем новые
                historyChart.data.datasets = [];
                data.datasets.forEach(dataset => {
                    historyChart.data.datasets.push({
                        label: dataset.label,
                        data: dataset.data,
                        borderColor: dataset.borderColor,
                        fill: false
                    });
                });
                historyChart.update();
                // Выводим проценты активности
                const statsDiv = document.getElementById('stats');
                statsDiv.innerHTML = '<h4>Процент активности:</h4>';
                for (const [target, percent] of Object.entries(data.stats)) {
                    statsDiv.innerHTML += `<p>${target}: ${percent}%</p>`;
                }
            });
    });
});
