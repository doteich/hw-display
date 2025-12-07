using LibreHardwareMonitor.Hardware;
using System.Net.Http.Json;
using System.Text.Json;

namespace HardwareMonitor;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly IConfiguration _configuration;
    private readonly HttpClient _httpClient;
    private readonly Computer _computer;

    public Worker(ILogger<Worker> logger, IConfiguration configuration, HttpClient httpClient)
    {
        _logger = logger;
        _configuration = configuration;
        _httpClient = httpClient;

        // Initialize LibreHardwareMonitor
        // We enable everything by default here, but specific data 
        // will be filtered before sending based on appsettings.
        _computer = new Computer
        {
            IsCpuEnabled = true,
            IsGpuEnabled = true,
            IsMemoryEnabled = true,
            IsMotherboardEnabled = true,
            IsControllerEnabled = true,
            IsNetworkEnabled = true,
            IsStorageEnabled = true
        };
    }

    public override Task StartAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Hardware Monitor Service starting...");
        try
        {
            _computer.Open();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to open hardware monitor. Note: This service requires Administrator privileges.");
        }
        return base.StartAsync(cancellationToken);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var targetUrl = _configuration["ApiSettings:EndpointUrl"] ?? "http://localhost:8080/stats";
        var intervalSeconds = _configuration.GetValue<int>("ApiSettings:IntervalSeconds", 60);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var payload = CollectHardwareData();

                if (payload.Any())
                {   
                    var cts = new CancellationTokenSource(TimeSpan.FromSeconds(20));
                    await PostDataAsync(targetUrl, payload, cts.Token);
                }
                else
                {
                    _logger.LogWarning("No hardware data collected. Check permissions or configuration.");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error occurred during monitoring cycle.");
            }

            await Task.Delay(TimeSpan.FromSeconds(intervalSeconds), stoppingToken);
        }
    }

    private List<HardwareMetric> CollectHardwareData()
    {
        var metrics = new List<HardwareMetric>();

        // Get configured sensor types to monitor (e.g., "Load", "Temperature", "Data")
        var allowedSensorTypes = _configuration.GetSection("Monitoring:SensorTypes").Get<string[]>()
                                 ?? Array.Empty<string>();

        // Iterate through all hardware
        foreach (var hardware in _computer.Hardware)
        {
            hardware.Update(); // Vital: Update sensor data

            // Sub-hardware (like CPU cores) might need recursion, 
            // but for top-level stats, this loop covers most needs.
            foreach (var sensor in hardware.Sensors)
            {

                // Console.WriteLine("HW: {0}, Name: {1}, Type {2}", hardware.Name, sensor.Name, sensor.SensorType.ToString());

                // Filter based on configuration
                if (allowedSensorTypes.Contains(sensor.SensorType.ToString()))
                {
                    if (sensor.Value.HasValue && sensor.Value > 0)
                    {
                        metrics.Add(new HardwareMetric
                        {
                            HardwareName = hardware.Name,
                            HardwareType = hardware.HardwareType.ToString(),
                            SensorName = sensor.Name,
                            SensorType = sensor.SensorType.ToString(),
                            Value = sensor.Value.Value
                        });
                    }
                }
            }
        }

        return metrics;
    }

    private async Task PostDataAsync(string url, List<HardwareMetric> data, CancellationToken token)
    {
        try
        {   
          

            var response = await _httpClient.PostAsJsonAsync(url, data, token);
            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("Successfully posted {Count} metrics to API.", data.Count);
            }
            else
            {
                _logger.LogWarning("API returned error: {StatusCode}", response.StatusCode);
            }
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError("Network error posting data: {Message}", ex.Message);
        }
    }

    public override Task StopAsync(CancellationToken cancellationToken)
    {
        _computer.Close();
        _logger.LogInformation("Hardware Monitor Service stopped.");
        return base.StopAsync(cancellationToken);
    }
}

// Simple DTO for JSON serialization
public class HardwareMetric
{
    public string HardwareName { get; set; } = "";
    public string HardwareType { get; set; } = "";
    public string SensorName { get; set; } = "";
    public string SensorType { get; set; } = "";
    public float Value { get; set; }
}