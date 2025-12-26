<?php

namespace App\Http\Controllers;

use App\Models\Chart;
use App\Services\VedicAstrologyService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class AstrologyController extends Controller
{
    protected VedicAstrologyService $astrologyService;

    public function __construct(VedicAstrologyService $astrologyService)
    {
        $this->astrologyService = $astrologyService;
    }

    /**
     * Show the main form
     */
    public function index()
    {
        $recentCharts = Chart::orderBy('created_at', 'desc')
            ->take(10)
            ->get();

        return view('astrology.index', compact('recentCharts'));
    }

    /**
     * Calculate and display chart
     */
    public function calculate(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'birth_date' => 'required|date',
            'birth_time' => 'required',
            'latitude' => 'required|numeric|between:-90,90',
            'longitude' => 'required|numeric|between:-180,180',
        ]);

        if ($validator->fails()) {
            return redirect()->back()
                ->withErrors($validator)
                ->withInput();
        }

        try {
            // Combine date and time
            $birthDatetime = $request->birth_date . ' ' . $request->birth_time;

            // Calculate chart
            $result = $this->astrologyService->calculateChart(
                $request->name,
                $birthDatetime,
                $request->latitude,
                $request->longitude
            );

            // Save to database
            $chart = Chart::create([
                'name' => $request->name,
                'birth_datetime' => $birthDatetime,
                'latitude' => $request->latitude,
                'longitude' => $request->longitude,
                'timezone' => 'UTC',
                'chart_data' => $result['chart'],
                'yogas_data' => $result['yogas']
            ]);

            return redirect()->route('astrology.chart', $chart->id);

        } catch (\Exception $e) {
            return redirect()->back()
                ->with('error', 'Failed to calculate chart: ' . $e->getMessage())
                ->withInput();
        }
    }

    /**
     * Show a specific chart
     */
    public function show(int $id)
    {
        $chart = Chart::findOrFail($id);

        return view('astrology.chart', compact('chart'));
    }

    /**
     * Ask AI a question (AJAX)
     */
    public function ask(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'chart_id' => 'required|integer|exists:charts,id',
            'question' => 'required|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $chart = Chart::findOrFail($request->chart_id);

            $answer = $this->astrologyService->getInterpretation(
                $chart->chart_data,
                'question',
                $request->question
            );

            return response()->json([
                'success' => true,
                'answer' => $answer
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to get answer: ' . $e->getMessage()
            ], 500);
        }
    }
}
