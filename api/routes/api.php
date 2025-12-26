<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ChartController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application.
| These routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group.
|
*/

// Vedic Astrology Chart API Routes
Route::prefix('chart')->group(function () {
    // Calculate birth chart
    Route::post('/calculate', [ChartController::class, 'calculate']);

    // Get saved chart
    Route::get('/{id}', [ChartController::class, 'show']);

    // Get all charts
    Route::get('/', [ChartController::class, 'index']);

    // Delete chart
    Route::delete('/{id}', [ChartController::class, 'destroy']);

    // Get AI interpretation
    Route::post('/interpret', [ChartController::class, 'interpret']);

    // Get dasha periods
    Route::post('/dasha', [ChartController::class, 'dasha']);

    // Get divisional chart
    Route::post('/divisional/{type}', [ChartController::class, 'divisionalChart']);

    // Detect yogas
    Route::post('/yogas', [ChartController::class, 'yogas']);

    // Ask AI a question about chart
    Route::post('/question', [ChartController::class, 'question']);

    // Get career guidance
    Route::post('/career', [ChartController::class, 'career']);

    // Get remedy suggestions
    Route::post('/remedies', [ChartController::class, 'remedies']);
});
