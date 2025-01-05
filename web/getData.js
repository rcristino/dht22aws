// Fetch data from the API
const apiUrl = 'MY_API_URL';
const apiKey = 'MY_API_KEY'; // API key obtained from API Gateway

// Variable to store the chart reference
let myChart = null;

// Function to create the chart with the fetched data
function createGraph(timestamps, temperatureData, humidityData) {
    // Destroy the existing chart if it exists
    if (myChart) {
        myChart.destroy();
    }

    const ctx = document.getElementById("temperatureHumidityChart").getContext("2d");

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [
                {
                    label: 'Temperature (Celsius)',
                    data: temperatureData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: 'Humidity (%)',
                    data: humidityData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time (UTC)', // Add "UTC" to the x-axis label
                        font: {
                            size: 14
                        }
                    },
                    ticks: {
                        maxRotation: 90, // Rotate ticks for better readability if needed
                        minRotation: 45
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Values'
                    }
                }
            }
        }
    });
}

// Function to prefill dates with defailt values
function prefillDates() {
    const now = new Date();
    const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); // 30 days ago

    // Function to format date as YYYY-MM-DDTHH:MM in UTC for datetime-local input
    function formatDateForInputUTC(date) {
        return date.toISOString().slice(0, 16);  // Slice to get only date and time, no milliseconds or timezone part
    }

    // Set the input values for start and end 
    document.getElementById('start').value = formatDateForInputUTC(thirtyDaysAgo); // 30 days ago
    document.getElementById('end').value = formatDateForInputUTC(now); // current time
}

// Function to load the graph with default dates
function loadGraph() {
    start = document.getElementById('start').value;
    end = document.getElementById('end').value;

    // Convert to Unix Timestamp (in seconds)
    const unixTimestampStart = Math.floor(new Date(start).getTime() / 1000);
    const unixTimestampEnd = Math.floor(new Date(end).getTime() / 1000);

    // Fetch data and update the graph
    fetchDataAndUpdateGraph(unixTimestampStart, unixTimestampEnd);
}

async function fetchDataAndUpdateGraph(start, end) {

    const deviceId = document.getElementById("deviceSelect").value;

    if (!deviceId) throw new Error('Required parameter missing!');

    let url = `${apiUrl}`;
    url += `?id=${encodeURIComponent(deviceId)}`;
    url += `&start=${encodeURIComponent(start)}`;
    url += `&end=${encodeURIComponent(end)}`;

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json', // Optional, if you're sending JSON data
                'X-Api-Key': apiKey, // Pass the API key in the header
            },
            mode: 'cors',  // Ensure CORS mode is set for cross-origin requests
        });

        if (!response.ok) throw new Error('Network Error: ' + response.body);

        const data = await response.json();

        // Sort the data by timestamp in ascending order
        data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        // Ensure onlu data from relevant deviceId is displayed
        const filteredData = data.filter(item => item.id === deviceId);

        // Extract the relevant data
        const timestamps = filteredData.map(item => item.timestamp.slice(0, 19).replace('T', ' '));
        const temperatures = filteredData.map(item => item.temperature);
        const humidities = filteredData.map(item => item.humidity);

        // Create the graph with the fetched data
        createGraph(timestamps, temperatures, humidities);

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Event listener for combobox change
document.getElementById("deviceSelect").addEventListener("change", () => {
    loadGraph();
  });
  
// Add event listener to the reset button to reset values to default
resetButton.addEventListener('click', function () {
    prefillDates();
    loadGraph();
});

// Call loadGraph on page load to prefill dates and load the graph
document.addEventListener("DOMContentLoaded", function () {
    prefillDates();
    loadGraph();  // This will load the graph with the default or URL-provided values
});
