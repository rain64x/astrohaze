<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('charts', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->dateTime('birth_datetime');
            $table->decimal('latitude', 10, 7);
            $table->decimal('longitude', 10, 7);
            $table->string('timezone')->default('UTC');
            $table->json('chart_data'); // Stores complete chart calculation
            $table->json('yogas_data')->nullable(); // Stores detected yogas
            $table->timestamps();

            // Indexes for better query performance
            $table->index('name');
            $table->index('birth_datetime');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('charts');
    }
};
