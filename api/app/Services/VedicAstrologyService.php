<?php

namespace App\Services;

use Exception;
use Illuminate\Support\Facades\Log;

class VedicAstrologyService
{
    /**
     * Path to Python executable
     */
    protected string $pythonPath;

    /**
     * Path to Python scripts directory
     */
    protected string $scriptsPath;

    public function __construct()
    {
        // Try to find python3
        $this->pythonPath = trim(shell_exec('which python3') ?: 'python3');
        $this->scriptsPath = base_path('../python');
    }

    /**
     * Calculate birth chart
     *
     * @param string $name
     * @param string $birthDatetime  ISO 8601 format
     * @param float $latitude
     * @param float $longitude
     * @return array
     * @throws Exception
     */
    public function calculateChart(
        string $name,
        string $birthDatetime,
        float $latitude,
        float $longitude
    ): array {
        $scriptPath = $this->scriptsPath . '/calculate_chart.php';

        // Create a temporary Python script to calculate the chart
        $pythonCode = $this->generateChartCalculationScript(
            $name,
            $birthDatetime,
            $latitude,
            $longitude
        );

        // Execute Python script and get results
        $result = $this->executePythonCode($pythonCode);

        return $result;
    }

    /**
     * Detect yogas in a chart
     *
     * @param array $chartData
     * @return array
     * @throws Exception
     */
    public function detectYogas(array $chartData): array
    {
        $pythonCode = $this->generateYogaDetectionScript($chartData);
        $result = $this->executePythonCode($pythonCode);

        return $result;
    }

    /**
     * Get AI interpretation
     *
     * @param array $chartData
     * @param string $type  (overview, career, remedies, etc.)
     * @param string|null $question
     * @return string
     * @throws Exception
     */
    public function getInterpretation(
        array $chartData,
        string $type = 'overview',
        ?string $question = null
    ): string {
        $pythonCode = $this->generateInterpretationScript($chartData, $type, $question);
        $result = $this->executePythonCode($pythonCode);

        return $result['interpretation'] ?? 'Unable to generate interpretation';
    }

    /**
     * Calculate divisional chart
     *
     * @param array $chartData
     * @param string $chartType  (D9, D10, D12, etc.)
     * @return array
     * @throws Exception
     */
    public function calculateDivisionalChart(array $chartData, string $chartType): array
    {
        $pythonCode = $this->generateDivisionalChartScript($chartData, $chartType);
        $result = $this->executePythonCode($pythonCode);

        return $result;
    }

    /**
     * Generate Python script for chart calculation
     */
    protected function generateChartCalculationScript(
        string $name,
        string $birthDatetime,
        float $latitude,
        float $longitude
    ): string {
        $datetime = json_encode($birthDatetime);
        $lat = $latitude;
        $lon = $longitude;

        return <<<PYTHON
import sys
sys.path.append('{$this->scriptsPath}')

from datetime import datetime
import pytz
from vedic_calculator import VedicCalculator
from yoga_detector import YogaDetector
import json

# Parse datetime
dt_str = {$datetime}
birth_dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

# Calculate chart
calculator = VedicCalculator()
chart_data = calculator.calculate_chart(birth_dt, {$lat}, {$lon})

# Detect yogas
yoga_detector = YogaDetector()
yogas_data = yoga_detector.detect_all_yogas(chart_data)

# Combine results
result = {
    'chart': chart_data,
    'yogas': yogas_data
}

# Output as JSON
print(json.dumps(result, default=str))
PYTHON;
    }

    /**
     * Generate Python script for yoga detection
     */
    protected function generateYogaDetectionScript(array $chartData): string
    {
        $chartJson = json_encode($chartData);

        return <<<PYTHON
import sys
sys.path.append('{$this->scriptsPath}')

from yoga_detector import YogaDetector
import json

# Parse chart data
chart_data = json.loads('''{$chartJson}''')

# Detect yogas
yoga_detector = YogaDetector()
yogas_data = yoga_detector.detect_all_yogas(chart_data)

# Output as JSON
print(json.dumps(yogas_data, default=str))
PYTHON;
    }

    /**
     * Generate Python script for AI interpretation
     */
    protected function generateInterpretationScript(
        array $chartData,
        string $type,
        ?string $question
    ): string {
        $chartJson = json_encode($chartData);
        $questionJson = json_encode($question);

        return <<<PYTHON
import sys
sys.path.append('{$this->scriptsPath}')

from ai_interpreter import AIInterpreter
import json

# Parse chart data
chart_data = json.loads('''{$chartJson}''')

# Initialize AI interpreter
ai = AIInterpreter()

# Get interpretation based on type
interpretation_type = '{$type}'

if interpretation_type == 'overview':
    interpretation = ai.interpret_chart_overview(chart_data)
elif interpretation_type == 'career':
    interpretation = ai.get_career_guidance(chart_data)
elif interpretation_type == 'remedies':
    interpretation = ai.suggest_remedies(chart_data)
elif interpretation_type == 'question':
    question = {$questionJson}
    interpretation = ai.answer_question(question, chart_data)
else:
    interpretation = 'Unknown interpretation type'

# Output as JSON
result = {'interpretation': interpretation}
print(json.dumps(result, default=str))
PYTHON;
    }

    /**
     * Generate Python script for divisional chart calculation
     */
    protected function generateDivisionalChartScript(array $chartData, string $chartType): string
    {
        $chartJson = json_encode($chartData);

        return <<<PYTHON
import sys
sys.path.append('{$this->scriptsPath}')

from divisional_charts import DivisionalCharts
import json

# Parse chart data
chart_data = json.loads('''{$chartJson}''')

# Calculate divisional chart
div_charts = DivisionalCharts()
div_chart = div_charts.calculate_divisional_chart(
    '{$chartType}',
    chart_data['planets']
)

# Output as JSON
print(json.dumps(div_chart, default=str))
PYTHON;
    }

    /**
     * Execute Python code and return JSON result
     *
     * @param string $pythonCode
     * @return array
     * @throws Exception
     */
    protected function executePythonCode(string $pythonCode): array
    {
        // Create temporary file for Python script
        $tempFile = tempnam(sys_get_temp_dir(), 'astro_');
        file_put_contents($tempFile, $pythonCode);

        try {
            // Execute Python script
            $command = "{$this->pythonPath} {$tempFile} 2>&1";
            $output = shell_exec($command);

            // Clean up
            unlink($tempFile);

            if ($output === null) {
                throw new Exception('Failed to execute Python script');
            }

            // Parse JSON output
            $result = json_decode($output, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                Log::error('Python script output: ' . $output);
                throw new Exception('Failed to parse Python output: ' . json_last_error_msg());
            }

            return $result;

        } catch (Exception $e) {
            // Clean up temp file if it still exists
            if (file_exists($tempFile)) {
                unlink($tempFile);
            }

            throw $e;
        }
    }
}
