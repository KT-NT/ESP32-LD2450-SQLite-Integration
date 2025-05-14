document.addEventListener('DOMContentLoaded', () => {
  let lastTimestamp = 0;

  // Переключение разделов
  document.getElementById('showLive').addEventListener('click', () => {
    document.getElementById('liveSection').style.display = 'block';
    document.getElementById('historySection').style.display = 'none';
  });
  document.getElementById('showHistory').addEventListener('click', () => {
    document.getElementById('liveSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'block';
  });

  // Инициализация live-графика
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

  // Периодический опрос live-API
  setInterval(() => {
    fetch(`/api/live?since=${lastTimestamp}`)
      .then(r => r.json())
      .then(json => {
        // Проходим по всем сериям из API
        json.datasets.forEach(ds => {
          // ищем уже существующую серию по label
          let existing = liveChart.data.datasets.find(d => d.label === ds.label);
          if (existing) {
            existing.data.push(...ds.data);
          } else {
            liveChart.data.datasets.push({
              label: ds.label,
              data: ds.data,
              borderColor: ds.borderColor,
              fill: false
            });
          }
        });
        // Обновляем метку времени
        lastTimestamp = json.since;
        liveChart.update();
      })
      .catch(console.error);
  }, 2000);

  // Инициализация графика истории
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

  // Загрузка истории по интервалу
  document.getElementById('loadHistory').addEventListener('click', () => {
    const start = document.getElementById('startTime').value;
    const end   = document.getElementById('endTime').value;
    if (!start || !end) {
      alert('Укажите начальное и конечное время');
      return;
    }
    fetch(`/api/history?start=${start}&end=${end}`)
      .then(r => r.json())
      .then(json => {
        // Очищаем старые данные
        historyChart.data.datasets = [];
        // Добавляем новые серии
        json.datasets.forEach(ds => {
          historyChart.data.datasets.push({
            label: ds.label,
            data: ds.data,
            borderColor: ds.borderColor,
            fill: false
          });
        });
        historyChart.update();
        // Выводим проценты активности
        const statsDiv = document.getElementById('stats');
        statsDiv.innerHTML = '<h4>Процент активности:</h4>';
        for (const [tgt, pct] of Object.entries(json.stats)) {
          statsDiv.innerHTML += `<p>${tgt}: ${pct}%</p>`;
        }
      })
      .catch(console.error);
  });
});
