<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Casts\Attribute;

class Chart extends Model
{
    use HasFactory;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'name',
        'birth_datetime',
        'latitude',
        'longitude',
        'timezone',
        'chart_data',
        'yogas_data',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'birth_datetime' => 'datetime',
        'latitude' => 'decimal:7',
        'longitude' => 'decimal:7',
        'chart_data' => 'array',
        'yogas_data' => 'array',
    ];

    /**
     * Get the planets from chart data
     */
    protected function planets(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->chart_data['planets'] ?? null,
        );
    }

    /**
     * Get the houses from chart data
     */
    protected function houses(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->chart_data['houses'] ?? null,
        );
    }

    /**
     * Get the dasha data from chart data
     */
    protected function dasha(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->chart_data['dasha'] ?? null,
        );
    }

    /**
     * Get the ascendant sign
     */
    protected function ascendantSign(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->chart_data['planets']['Ascendant']['sign'] ?? null,
        );
    }

    /**
     * Get the moon sign
     */
    protected function moonSign(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->chart_data['planets']['Moon']['sign'] ?? null,
        );
    }

    /**
     * Get the sun sign
     */
    protected function sunSign(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->chart_data['planets']['Sun']['sign'] ?? null,
        );
    }
}
