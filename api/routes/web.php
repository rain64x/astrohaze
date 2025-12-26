<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AstrologyController;

Route::get('/', function () {
    return redirect()->route('astrology.index');
});

// Astrology Web Interface
Route::prefix('astrology')->name('astrology.')->group(function () {
    Route::get('/', [AstrologyController::class, 'index'])->name('index');
    Route::post('/calculate', [AstrologyController::class, 'calculate'])->name('calculate');
    Route::get('/chart/{id}', [AstrologyController::class, 'show'])->name('chart');
    Route::post('/ask', [AstrologyController::class, 'ask'])->name('ask');
});
