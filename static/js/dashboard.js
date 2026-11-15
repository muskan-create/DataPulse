
/* =====================================================
   DATAPULSE — DASHBOARD JAVASCRIPT
   Dark Navy | Blue Analytics
   Charts | Upload | Animations
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* =========================================
       1. READ DASHBOARD DATA
    ========================================= */

    const dataElement = document.getElementById(
        "dashboard-chart-data"
    );

    let dashboardData = {};

    if (dataElement) {
        try {
            dashboardData = JSON.parse(
                dataElement.textContent
            );
        } catch (error) {
            console.error(
                "Dashboard data could not be loaded:",
                error
            );
        }
    }

    const charts = dashboardData || {};


    /* =========================================
       2. DARK NAVY CHART COLORS
    ========================================= */

    const palette = {
        blue: "#3B82F6",
        lightBlue: "#60A5FA",
        cyan: "#22D3EE",
        purple: "#A78BFA",
        green: "#34D399",
        yellow: "#FBBF24",
        pink: "#F472B6",
        orange: "#FB923C",
        background: "#1B2940",
        dark: "#111C2E",
        text: "#F1F5F9",
        muted: "#94A3B8",
        border: "#2B3A50"
    };

    const colors = [
        palette.blue,
        palette.cyan,
        palette.purple,
        palette.green,
        palette.yellow,
        palette.pink,
        palette.orange,
        palette.lightBlue
    ];


    /* =========================================
       3. CHART DEFAULT SETTINGS
    ========================================= */

    if (typeof Chart === "undefined") {
        console.error(
            "Chart.js is not loaded. Check base.html."
        );
        return;
    }

    Chart.defaults.font.family =
        "'DM Sans', sans-serif";

    Chart.defaults.font.size = 11;
    Chart.defaults.color = palette.muted;

    Chart.defaults.plugins.legend.labels.usePointStyle =
        true;

    Chart.defaults.plugins.legend.labels.padding = 15;

    Chart.defaults.animation.duration = 1000;
    Chart.defaults.animation.easing = "easeOutQuart";


    /* =========================================
       4. DATA HELPERS
    ========================================= */

    function getCanvas(id) {
        return document.getElementById(id);
    }

    function getLabels(data) {
        return Array.isArray(data?.labels)
            ? data.labels
            : [];
    }

    function getValues(data) {
        return Array.isArray(data?.values)
            ? data.values
            : [];
    }

    function hasData(data) {
        return (
            getLabels(data).length > 0 &&
            getValues(data).length > 0
        );
    }


    /* =========================================
       5. CHART GRADIENT
    ========================================= */

    function makeGradient(ctx, color) {

        const gradient = ctx.createLinearGradient(
            0,
            0,
            0,
            300
        );

        gradient.addColorStop(
            0,
            color + "55"
        );

        gradient.addColorStop(
            1,
            color + "03"
        );

        return gradient;
    }


    /* =========================================
       6. COMMON CHART OPTIONS
    ========================================= */

    function getCommonOptions(type, options = {}) {

        const isCircular =
            type === "doughnut" ||
            type === "pie";

        return {

            responsive: true,

            maintainAspectRatio: false,

            animation: {
                duration: 1100,
                easing: "easeOutQuart"
            },

            interaction: {
                intersect: false,
                mode: "index"
            },

            plugins: {

                legend: {
                    display: options.legend !== false,
                    position: "bottom",

                    labels: {
                        color: palette.muted,
                        usePointStyle: true,
                        padding: 16
                    }
                },

                tooltip: {
                    backgroundColor: "#111C2E",
                    titleColor: palette.text,
                    bodyColor: palette.text,
                    borderColor: palette.border,
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 9,
                    displayColors: true
                }
            },

            scales: isCircular ? {} : {

                x: {
                    grid: {
                        display: false
                    },

                    border: {
                        display: false
                    },

                    ticks: {
                        color: palette.muted,
                        maxRotation: 35,
                        minRotation: 0
                    }
                },

                y: {
                    beginAtZero: true,

                    grid: {
                        color: "rgba(148, 163, 184, 0.12)"
                    },

                    border: {
                        display: false,
                        dash: [4, 4]
                    },

                    ticks: {
                        color: palette.muted
                    }
                }
            }
        };
    }


    /* =========================================
       7. CREATE STANDARD CHART
    ========================================= */

    function createChart(
        id,
        data,
        type,
        options = {}
    ) {

        const canvas = getCanvas(id);

        if (!canvas || !hasData(data)) {
            return null;
        }

        const ctx = canvas.getContext("2d");

        const chartColor =
            options.color || palette.blue;

        const dataset = {

            label: options.label || "Value",

            data: getValues(data),

            borderColor: chartColor,

            backgroundColor: type === "line"
                ? makeGradient(ctx, chartColor)
                : options.backgroundColor || chartColor,

            borderWidth: type === "line" ? 3 : 1,

            borderRadius: type === "bar" ? 6 : 0,

            tension: 0.4,

            fill: type === "line",

            pointRadius: type === "line" ? 4 : 0,

            pointHoverRadius: 7,

            pointBackgroundColor: chartColor,

            pointBorderColor: "#1B2940",

            pointBorderWidth: 2
        };

        if (options.multipleColors) {
            dataset.backgroundColor = colors;
            dataset.borderColor = "#1B2940";
            dataset.borderWidth = 2;
        }

        const config = {

            type: type,

            data: {
                labels: getLabels(data),
                datasets: [dataset]
            },

            options: getCommonOptions(type, options)
        };

        if (options.horizontal) {
            config.options.indexAxis = "y";
        }

        return new Chart(ctx, config);
    }


    /* =========================================
       8. SPECIAL LINE CHART FOR TREND ANALYTICS
       Revenue | Profit | Orders
    ========================================= */

    function createTrendChart(
        id,
        data,
        label,
        color
    ) {

        const canvas = getCanvas(id);

        if (!canvas || !data) {
            console.warn("Trend chart missing:", id);
            return;
        }

        const labels = getLabels(data);
        const values = getValues(data);

        const validData = labels

            .map((item, index) => ({
                label: item,
                value: Number(values[index])
            }))

            .filter(item =>
                Number.isFinite(item.value)
            );

        if (validData.length === 0) {
            console.warn("No valid trend data:", id);
            return;
        }

        new Chart(canvas.getContext("2d"), {

            type: "line",

            data: {

                labels: validData.map(item => item.label),

                datasets: [{

                    label: label,

                    data: validData.map(item => item.value),

                    borderColor: color,

                    backgroundColor: color + "20",

                    borderWidth: 3,

                    tension: 0.35,

                    fill: true,

                    spanGaps: true,

                    pointRadius: 4,

                    pointHoverRadius: 7,

                    pointBackgroundColor: color,

                    pointBorderColor: "#1B2940",

                    pointBorderWidth: 2
                }]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                animation: {
                    duration: 1000
                },

                interaction: {
                    intersect: false,
                    mode: "index"
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        enabled: true,

                        backgroundColor: "#111C2E",

                        titleColor: "#F1F5F9",

                        bodyColor: "#F1F5F9",

                        borderColor: "#2B3A50",

                        borderWidth: 1,

                        padding: 12
                    }
                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        },

                        border: {
                            display: false
                        },

                        ticks: {
                            color: "#94A3B8",
                            maxRotation: 0,
                            autoSkip: true
                        }
                    },

                    y: {

                        beginAtZero: true,

                        grid: {
                            color: "rgba(148,163,184,0.12)"
                        },

                        border: {
                            display: false
                        },

                        ticks: {
                            color: "#94A3B8"
                        }
                    }
                }
            }
        });

        console.log(
            id,
            "rendered successfully:",
            validData
        );
    }


    /* =========================================
       9. REVENUE TREND
    ========================================= */

    createTrendChart(
        "revenueTrendChart",
        charts.trend,
        "Revenue",
        palette.blue
    );


    /* =========================================
       10. PRODUCT PERFORMANCE
    ========================================= */

    createChart(
        "productChart",
        charts.product,
        "bar",
        {
            label: "Product Revenue",
            color: palette.lightBlue,
            legend: false
        }
    );


    /* =========================================
       11. REGIONAL PERFORMANCE
    ========================================= */

    createChart(
        "regionChart",
        charts.region,
        "doughnut",
        {
            label: "Regional Performance",
            multipleColors: true
        }
    );


    /* =========================================
       12. CATEGORY DISTRIBUTION
    ========================================= */

    createChart(
        "categoryChart",
        charts.category_count,
        "bar",
        {
            label: "Category Distribution",
            multipleColors: true,
            legend: false
        }
    );


    /* =========================================
       13. VALUE DISTRIBUTION
    ========================================= */

    createChart(
        "distributionChart",
        charts.histogram,
        "bar",
        {
            label: "Value Distribution",
            color: palette.purple,
            legend: false
        }
    );


    /* =========================================
       14. REVENUE VS PROFIT
    ========================================= */

    function createScatterChart() {

        const canvas = getCanvas("scatterChart");

        if (!canvas || !charts.scatter) {
            return;
        }

        const points = charts.scatter.points || [];

        if (!points.length) {
            return;
        }

        const validPoints = points

            .map(point => {

                if (Array.isArray(point)) {
                    return {
                        x: Number(point[0]),
                        y: Number(point[1])
                    };
                }

                return {
                    x: Number(point.x),
                    y: Number(point.y)
                };
            })

            .filter(point => {

                return (
                    Number.isFinite(point.x) &&
                    Number.isFinite(point.y)
                );
            });

        if (!validPoints.length) {
            return;
        }

        new Chart(canvas.getContext("2d"), {

            type: "scatter",

            data: {

                datasets: [{

                    label: "Revenue vs Profit",

                    data: validPoints,

                    backgroundColor: palette.cyan,

                    borderColor: palette.lightBlue,

                    borderWidth: 1,

                    pointRadius: 5,

                    pointHoverRadius: 8
                }]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                animation: {
                    duration: 1100
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        backgroundColor: palette.dark,

                        titleColor: palette.text,

                        bodyColor: palette.text,

                        borderColor: palette.border,

                        borderWidth: 1,

                        padding: 12
                    }
                },

                scales: {

                    x: {

                        type: "linear",

                        position: "bottom",

                        title: {

                            display: true,

                            text: charts.scatter.x_label ||
                                "Revenue",

                            color: palette.muted
                        },

                        ticks: {
                            color: palette.muted
                        },

                        grid: {
                            color: "rgba(148, 163, 184, 0.12)"
                        }
                    },

                    y: {

                        title: {

                            display: true,

                            text: charts.scatter.y_label ||
                                "Profit",

                            color: palette.muted
                        },

                        ticks: {
                            color: palette.muted
                        },

                        grid: {
                            color: "rgba(148, 163, 184, 0.12)"
                        }
                    }
                }
            }
        });
    }

    createScatterChart();


    /* =========================================
       15. PROFIT TREND
    ========================================= */

    createTrendChart(
        "profitTrendChart",
        charts.profit_trend,
        "Profit",
        palette.green
    );


    /* =========================================
       16. ORDERS TREND
    ========================================= */

    createTrendChart(
        "ordersTrendChart",
        charts.orders_trend,
        "Orders",
        palette.yellow
    );


    /* =========================================
       17. FILE NAME PREVIEW
    ========================================= */

    function setupFilePreview(inputId, labelId) {

        const input = document.getElementById(inputId);

        const label = document.getElementById(labelId);

        if (!input) {
            return;
        }

        input.addEventListener("change", function () {

            const file = this.files && this.files[0];

            if (file && label) {
                label.textContent = file.name;
            }
        });
    }

    setupFilePreview(
        "dashboard-file",
        "dashboard-file-name"
    );

    setupFilePreview(
        "dashboard-file-empty",
        "dashboard-file-empty-name"
    );


    /* =========================================
       18. EMPTY DASHBOARD UPLOAD
    ========================================= */

    const emptyInput = document.getElementById(
        "dashboard-file-empty"
    );

    if (emptyInput) {

        emptyInput.addEventListener("change", function () {

            if (!this.files || !this.files.length) {
                return;
            }

            const form = this.closest("form");

            if (form) {
                form.requestSubmit();
            }
        });
    }


    /* =========================================
       19. UPLOAD BUTTON LOADING STATE
    ========================================= */

    document.querySelectorAll(
        ".dashboard-page form"
    ).forEach(form => {

        form.addEventListener("submit", function () {

            const button = this.querySelector(
                'button[type="submit"]'
            );

            if (button) {

                button.dataset.originalText =
                    button.textContent;

                button.textContent = "Uploading...";

                button.disabled = true;
            }
        });
    });


    /* =========================================
       20. ANIMATED NUMBER COUNTERS
    ========================================= */

    function animateCounters() {

        const counters = document.querySelectorAll(
            ".dashboard-page [data-count]"
        );

        counters.forEach(counter => {

            const target = Number(counter.dataset.count);

            if (!Number.isFinite(target)) {
                return;
            }

            const duration = 1000;

            const startTime = performance.now();

            function update(currentTime) {

                const progress = Math.min(
                    (currentTime - startTime) / duration,
                    1
                );

                const eased =
                    1 - Math.pow(1 - progress, 3);

                const value = target * eased;

                counter.textContent = Number.isInteger(target)

                    ? Math.round(value).toLocaleString("en-IN")

                    : value.toLocaleString("en-IN", {
                        maximumFractionDigits: 2
                    });

                if (progress < 1) {
                    requestAnimationFrame(update);
                }
            }

            requestAnimationFrame(update);
        });
    }

    animateCounters();


    /* =========================================
       21. INITIALIZATION STATUS
    ========================================= */

    console.log(
        "DataPulse Dashboard initialized successfully."
    );

    console.log(
        "Available chart data:",
        Object.keys(charts)
    );

});
