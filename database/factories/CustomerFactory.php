<?php

namespace Database\Factories;

use App\Models\Customer;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Customer>
 */
class CustomerFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'name' => fake('tr_TR')->name(),
            'email' => fake()->unique()->safeEmail(),
            'phone' => '555'.fake()->numerify('#######'),
            'city' => fake()->randomElement([
                'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana',
                'Konya', 'Gaziantep', 'Kayseri', 'Eskişehir', 'Trabzon', 'Samsun',
            ]),
        ];
    }
}
