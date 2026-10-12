<?php

namespace Database\Factories;

use App\Models\Customer;
use App\Models\Order;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Order>
 */
class OrderFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $createdAt = fake()->dateTimeBetween('-6 months');

        return [
            'customer_id' => Customer::factory(),
            'order_number' => 'ORD-'.fake()->unique()->numberBetween(10000, 99999),
            'total_amount' => fake()->randomFloat(2, 50, 10000),
            'status' => fake()->randomElement(['pending', 'processing', 'completed', 'cancelled']),
            'notes' => fake()->optional(0.6)->randomElement([
                'Kapıda ödeme seçildi.',
                'Hızlı kargo talep edildi.',
                'Havale bekleniyor.',
                'Hediye paketi yapıldı.',
                'Fatura adresi farklı.',
                'Müşteri teslimat öncesi aranmalı.',
                'Kargo şubeden teslim alınacak.',
                'İade talebi oluşturuldu.',
            ]),
            'created_at' => $createdAt,
            'updated_at' => $createdAt,
        ];
    }
}
