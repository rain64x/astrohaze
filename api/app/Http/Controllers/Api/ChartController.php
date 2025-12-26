<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Chart;
use App\Services\VedicAstrologyService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;

class ChartController extends Controller
{
    protected VedicAstrologyService $astrologyService;

    public function __construct(VedicAstrologyService $astrologyService)
    {
        $this->astrologyService = $astrologyService;
    }

    /**
     * Get all charts
     */
    public function index(): JsonResponse
    {
        $charts = Chart::orderBy('created_at', 'desc')
            ->get()
            ->map(function ($chart) {
                return [
                    'id' => $chart->id,
                    'name' => $chart->name,
                    'birth_datetime' => $chart->birth_datetime,
                    'ascendant_sign' => $chart->ascendant_sign,
                    'moon_sign' => $chart->moon_sign,
                    'sun_sign' => $chart->sun_sign,
                    'created_at' => $chart->created_at,
                ];
            });

        return response()->json([
            'success' => true,
            'data' => $charts
        ]);
    }

    /**
     * Get a specific chart
     */
    public function show(int $id): JsonResponse
    {
        $chart = Chart::find($id);

        if (!$chart) {
            return response()->json([
                'success' => false,
                'message' => 'Chart not found'
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $chart
        ]);
    }

    /**
     * Calculate a new birth chart
     */
    public function calculate(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'birth_datetime' => 'required|date',
            'latitude' => 'required|numeric|between:-90,90',
            'longitude' => 'required|numeric|between:-180,180',
            'timezone' => 'nullable|string',
            'save' => 'nullable|boolean'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            // Calculate chart using Python service
            $result = $this->astrologyService->calculateChart(
                $request->name,
                $request->birth_datetime,
                $request->latitude,
                $request->longitude
            );

            // Optionally save to database
            $chart = null;
            if ($request->save ?? true) {
                $chart = Chart::create([
                    'name' => $request->name,
                    'birth_datetime' => $request->birth_datetime,
                    'latitude' => $request->latitude,
                    'longitude' => $request->longitude,
                    'timezone' => $request->timezone ?? 'UTC',
                    'chart_data' => $result['chart'],
                    'yogas_data' => $result['yogas']
                ]);
            }

            return response()->json([
                'success' => true,
                'data' => [
                    'chart_id' => $chart?->id,
                    'chart' => $result['chart'],
                    'yogas' => $result['yogas']
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to calculate chart',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Delete a chart
     */
    public function destroy(int $id): JsonResponse
    {
        $chart = Chart::find($id);

        if (!$chart) {
            return response()->json([
                'success' => false,
                'message' => 'Chart not found'
            ], 404);
        }

        $chart->delete();

        return response()->json([
            'success' => true,
            'message' => 'Chart deleted successfully'
        ]);
    }

    /**
     * Get AI interpretation of a chart
     */
    public function interpret(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required_without:chart_data|integer|exists:charts,id',
            'chart_data' => 'required_without:chart_id|array',
            'type' => 'nullable|string|in:overview,career,remedies'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            // Get chart data
            $chartData = $this->getChartData($request);

            // Get interpretation
            $interpretation = $this->astrologyService->getInterpretation(
                $chartData,
                $request->type ?? 'overview'
            );

            return response()->json([
                'success' => true,
                'data' => [
                    'interpretation' => $interpretation,
                    'type' => $request->type ?? 'overview'
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to generate interpretation',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get dasha periods
     */
    public function dasha(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required_without:chart_data|integer|exists:charts,id',
            'chart_data' => 'required_without:chart_id|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $chartData = $this->getChartData($request);

            return response()->json([
                'success' => true,
                'data' => $chartData['dasha'] ?? []
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to get dasha data',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Calculate divisional chart
     */
    public function divisionalChart(Request $request, string $type): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required_without:chart_data|integer|exists:charts,id',
            'chart_data' => 'required_without:chart_id|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        // Validate chart type
        $validTypes = ['D9', 'D10', 'D12', 'D7', 'D16', 'D20', 'D24', 'D30', 'D60'];
        $chartType = strtoupper($type);

        if (!in_array($chartType, $validTypes)) {
            return response()->json([
                'success' => false,
                'message' => 'Invalid divisional chart type. Valid types: ' . implode(', ', $validTypes)
            ], 422);
        }

        try {
            $chartData = $this->getChartData($request);

            $divChart = $this->astrologyService->calculateDivisionalChart(
                $chartData,
                $chartType
            );

            return response()->json([
                'success' => true,
                'data' => $divChart
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to calculate divisional chart',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Detect yogas in a chart
     */
    public function yogas(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required_without:chart_data|integer|exists:charts,id',
            'chart_data' => 'required_without:chart_id|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $chartData = $this->getChartData($request);

            $yogas = $this->astrologyService->detectYogas($chartData);

            return response()->json([
                'success' => true,
                'data' => $yogas
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to detect yogas',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Ask AI a question about the chart
     */
    public function question(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required_without:chart_data|integer|exists:charts,id',
            'chart_data' => 'required_without:chart_id|array',
            'question' => 'required|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $chartData = $this->getChartData($request);

            $answer = $this->astrologyService->getInterpretation(
                $chartData,
                'question',
                $request->question
            );

            return response()->json([
                'success' => true,
                'data' => [
                    'question' => $request->question,
                    'answer' => $answer
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to answer question',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get career guidance
     */
    public function career(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required_without:chart_data|integer|exists:charts,id',
            'chart_data' => 'required_without:chart_id|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $chartData = $this->getChartData($request);

            $guidance = $this->astrologyService->getInterpretation(
                $chartData,
                'career'
            );

            return response()->json([
                'success' => true,
                'data' => [
                    'guidance' => $guidance
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to get career guidance',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get remedy suggestions
     */
    public function remedies(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required_without:chart_data|integer|exists:charts,id',
            'chart_data' => 'required_without:chart_data|array',
            'issue' => 'nullable|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $chartData = $this->getChartData($request);

            $remedies = $this->astrologyService->getInterpretation(
                $chartData,
                'remedies',
                $request->issue
            );

            return response()->json([
                'success' => true,
                'data' => [
                    'remedies' => $remedies,
                    'issue' => $request->issue
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to get remedy suggestions',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Helper: Get chart data from request (either from ID or direct data)
     */
    protected function getChartData(Request $request): array
    {
        if ($request->has('chart_id')) {
            $chart = Chart::findOrFail($request->chart_id);
            return $chart->chart_data;
        }

        return $request->chart_data;
    }
}
