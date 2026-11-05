/* LeafCare AI - Interactive Dashboard Charts */

document.addEventListener('DOMContentLoaded', async () => {
  const healthCtx = document.getElementById('healthRatioChart')?.getContext('2d');
  const cropsCtx = document.getElementById('cropsBarChart')?.getContext('2d');

  if (!healthCtx || !cropsCtx) return;

  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    // 1. Health Ratio Doughnut Chart
    new Chart(healthCtx, {
      type: 'doughnut',
      data: {
        labels: ['Healthy Foliage', 'Diseased Leaves'],
        datasets: [{
          data: [data.healthy_scans, data.diseased_scans],
          backgroundColor: ['#52b788', '#e63946'],
          hoverBackgroundColor: ['#2d6a4f', '#d90429'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 14,
              font: { family: 'Plus Jakarta Sans', weight: '600' }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const total = data.total_scans || 1;
                const val = context.raw || 0;
                const pct = ((val / total) * 100).toFixed(1);
                return ` ${context.label}: ${val} (${pct}%)`;
              }
            }
          }
        },
        cutout: '68%'
      }
    });

    // 2. Crops Breakdown Bar Chart
    const cropLabels = data.plants_breakdown.map(p => p.name);
    const cropCounts = data.plants_breakdown.map(p => p.count);

    new Chart(cropsCtx, {
      type: 'bar',
      data: {
        labels: cropLabels.length ? cropLabels : ['No Crops Yet'],
        datasets: [{
          label: 'Diagnoses Count',
          data: cropCounts.length ? cropCounts : [0],
          backgroundColor: '#40916c',
          hoverBackgroundColor: '#1b4332',
          borderRadius: 8,
          barPercentage: 0.6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
              font: { family: 'Plus Jakarta Sans' }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.04)'
            }
          },
          x: {
            ticks: {
              font: { family: 'Plus Jakarta Sans', weight: '600' }
            },
            grid: { display: false }
          }
        }
      }
    });

  } catch (err) {
    console.error('Failed to load dashboard chart data:', err);
  }
});
