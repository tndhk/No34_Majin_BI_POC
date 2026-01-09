import json
import time
from collections.abc import Callable

import pandas as pd

from src.services.ai_generator import GenerationResult


class MockAIGenerator:
    """
    APIコストを節約するためのモックジェネレーター。
    Titanicデータセットに基づいた「Executive Theme」のダッシュボードを即座に返します。
    """

    def generate_oneshot(
        self, df: pd.DataFrame, progress_callback: Callable[[int, str], None] | None = None
    ) -> GenerationResult:
        """
        モックデータを生成して返します。入力DFは無視されます。
        """
        print("MOCK MODE: Generating executive dashboard without API call...")

        if progress_callback:
            progress_callback(1, "デモデータを準備中...")
            time.sleep(0.5)
            progress_callback(2, "エグゼクティブ・インサイトを抽出中...")
            time.sleep(0.5)
            progress_callback(3, "ビジュアリゼーションを構築中...")
            time.sleep(0.5)
            progress_callback(4, "完了")

        # 1. Mock JSON Data (Executive Insight)
        mock_data = {
            "kpi": {
                "total_passengers": 891,
                "survival_rate": "38.4%",
                "avg_fare": "$32.20",
                "first_class_survival": "62.9%",
            },
            "charts": {
                "survival_by_class": {
                    "labels": ["1st Class", "2nd Class", "3rd Class"],
                    "datasets": [
                        {"label": "Survival Rate", "data": [62.9, 47.3, 24.2], "type": "bar"}
                    ],
                },
                "survival_by_gender": {
                    "labels": ["Female", "Male"],
                    "datasets": [{"label": "Survivors", "data": [233, 109], "type": "doughnut"}],
                },
                "age_distribution": {
                    "labels": ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "60+"],
                    "datasets": [
                        {
                            "label": "Passenger Count",
                            "data": [64, 115, 230, 155, 86, 42, 22],
                            "type": "line",
                            "fill": True,
                        }
                    ],
                },
                "fare_analysis": {
                    "labels": ["S", "C", "Q"],
                    "datasets": [
                        {"label": "Average Fare", "data": [27.07, 59.95, 13.27], "type": "radar"}
                    ],
                },
            },
            "insight_summary": "Overall survival rate was 38.4%. First-class passengers had a significantly higher survival chance (62.9%) compared to 3rd class (24.2%). Females were prioritized in rescue operations.",
        }

        # 2. Mock Python Code (Just for display)

        # 3. Mock HTML Template (Executive Theme applied)
        mock_html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Majin Executive Dashboard (Demo)</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>

    <style>
        :root {
            /* Base Colors - Deep Executive Navy */
            --void-deep: #0b1120;
            --void-surface: #151e32;
            --void-elevated: #1e293b;
            --void-border: #334155;

            /* Accent Colors - Professional Trust */
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;

            --oracle-colors: #38bdf8, #fbbf24, #818cf8, #34d399, #f472b6, #2dd4bf;
        }

        body {
            background-color: var(--void-deep);
            color: var(--text-primary);
            font-family: 'DM Sans', sans-serif;
            padding: 2rem;
        }

        h1, h2, h3 { font-family: 'Cormorant Garamond', serif; }

        .card {
            background-color: var(--void-surface);
            border: 1px solid var(--void-border);
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }

        .metric-value {
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>

    <script>
        // Chart.js Global Defaults
        Chart.defaults.color = '#cbd5e1';
        Chart.defaults.borderColor = '#334155';
        Chart.defaults.font.family = "'DM Sans', sans-serif";

        const ORACLE_COLORS = [
            '#38bdf8', '#fbbf24', '#818cf8', '#34d399', '#f472b6',
            '#2dd4bf', '#a78bfa', '#fb923c', '#9ca3af', '#60a5fa'
        ];

        // 【必須】カラー適用ヘルパー関数
        function assignOracleColors(chartData, index) {
            const color = ORACLE_COLORS[index % ORACLE_COLORS.length];
            chartData.datasets.forEach(ds => {
                if (ds.type === 'pie' || ds.type === 'doughnut' || (!ds.type && chartData.labels.length > 1 && !chartData.datasets[0].label)) {
                     // 円グラフなど
                    ds.backgroundColor = ORACLE_COLORS;
                    ds.borderColor = '#1e293b';
                } else {
                    // 棒グラフなど
                    ds.backgroundColor = color;
                    ds.borderColor = color;
                }
            });
            return chartData;
        }
    </script>
</head>
<body class="min-h-screen">
    <div class="max-w-7xl mx-auto">
        <header class="mb-8 border-b border-gray-800 pb-4">
            <h1 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">
                Titanic Executive Metadata
            </h1>
            <p class="text-slate-400 mt-2">Demo Mode: Verified Design System</p>
        </header>

        <!-- KPI Area -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="card">
                <h3 class="text-slate-400 text-sm uppercase tracking-wider">Total Passengers</h3>
                <p class="metric-value" id="kpi-total">-</p>
            </div>
            <div class="card">
                <h3 class="text-slate-400 text-sm uppercase tracking-wider">Survival Rate</h3>
                <p class="metric-value" id="kpi-survival">-</p>
            </div>
            <div class="card">
                <h3 class="text-slate-400 text-sm uppercase tracking-wider">Avg Fare</h3>
                <p class="metric-value" id="kpi-fare">-</p>
            </div>
            <div class="card">
                <h3 class="text-slate-400 text-sm uppercase tracking-wider">1st Class Survival</h3>
                <p class="metric-value" id="kpi-class1">-</p>
            </div>
        </div>

        <!-- Charts Area -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Chart 1 -->
            <div class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold text-slate-100">Survival by Class</h3>
                    <i data-lucide="bar-chart-2" class="text-sky-400"></i>
                </div>
                <div class="relative h-64">
                    <canvas id="chart1"></canvas>
                </div>
                <p class="mt-4 text-sm text-slate-400 italic bg-gray-900/50 p-3 rounded border-l-2 border-sky-400">
                    Highest survival rate observed in 1st class passengers.
                </p>
            </div>

            <!-- Chart 2 -->
            <div class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold text-slate-100">Survival by Gender</h3>
                    <i data-lucide="pie-chart" class="text-amber-400"></i>
                </div>
                <div class="relative h-64">
                    <canvas id="chart2"></canvas>
                </div>
            </div>

            <!-- Chart 3 -->
            <div class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold text-slate-100">Age Distribution</h3>
                    <i data-lucide="activity" class="text-emerald-400"></i>
                </div>
                <div class="relative h-64">
                    <canvas id="chart3"></canvas>
                </div>
            </div>

            <!-- Chart 4 -->
            <div class="card">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold text-slate-100">Fare by Embarkation</h3>
                    <i data-lucide="radar" class="text-indigo-400"></i>
                </div>
                <div class="relative h-64">
                    <canvas id="chart4"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- Injection Script -->
    <script>
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', function() {
            lucide.createIcons();

            // Injected Data (will be replaced by Python)
            const dashboardData = {{JSON_DATA}};

            const ORACLE_COLORS_RUNTIME = [
                '#38bdf8', '#fbbf24', '#818cf8', '#34d399', '#f472b6',
                '#2dd4bf', '#a78bfa', '#fb923c', '#9ca3af', '#60a5fa'
            ];

            function applyColors(chartData, index) {
                const color = ORACLE_COLORS_RUNTIME[index % ORACLE_COLORS_RUNTIME.length];
                chartData.datasets.forEach(ds => {
                    if (ds.type === 'pie' || ds.type === 'doughnut') {
                        ds.backgroundColor = ORACLE_COLORS_RUNTIME;
                        ds.borderColor = '#1e293b';
                    } else {
                        ds.backgroundColor = color;
                        ds.borderColor = color;
                    }
                });
                return chartData;
            }

            // Populate KPIs
            document.getElementById('kpi-total').textContent = dashboardData.kpi.total_passengers;
            document.getElementById('kpi-survival').textContent = dashboardData.kpi.survival_rate;
            document.getElementById('kpi-fare').textContent = dashboardData.kpi.avg_fare;
            document.getElementById('kpi-class1').textContent = dashboardData.kpi.first_class_survival;

            // Chart 1: Bar
            const ctx1 = document.getElementById('chart1').getContext('2d');
            new Chart(ctx1, {
                type: 'bar',
                data: applyColors(dashboardData.charts.survival_by_class, 0),
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

            // Chart 2: Doughnut
            const ctx2 = document.getElementById('chart2').getContext('2d');
            new Chart(ctx2, {
                type: 'doughnut',
                data: applyColors(dashboardData.charts.survival_by_gender, 1),
                options: { responsive: true, maintainAspectRatio: false }
            });

            // Chart 3: Line
            const ctx3 = document.getElementById('chart3').getContext('2d');
            new Chart(ctx3, {
                type: 'line',
                data: applyColors(dashboardData.charts.age_distribution, 3),
                options: { responsive: true, maintainAspectRatio: false, tension: 0.4 }
            });

            // Chart 4: Radar
            const ctx4 = document.getElementById('chart4').getContext('2d');
            new Chart(ctx4, {
                type: 'radar',
                data: applyColors(dashboardData.charts.fare_analysis, 2),
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            grid: { color: '#334155' },
                            angleLines: { color: '#334155' },
                            pointLabels: { color: '#cbd5e1' }
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>
"""
        # Inject JSON into HTML locally to mimic AIGenerator.assemble_html
        assembled_html = mock_html.replace("{{JSON_DATA}}", json.dumps(mock_data))

        return GenerationResult(
            html=assembled_html,
            data=mock_data,
            blueprint="## Mock Blueprint\n- This is a pre-defined demo blueprint.",
        )
