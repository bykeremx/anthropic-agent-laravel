<?php

namespace Database\Seeders;

use App\Models\Customer;
use App\Models\Order;
use Illuminate\Database\Seeder;

class OrderSeeder extends Seeder
{
    /**
     * 100 sipariş: db-schema.md'deki 4 örnek sipariş (ORD-1001..1004) + 96 rastgele sipariş (ORD-1005..1100).
     */
    public function run(): void
    {
        $customers = Customer::orderBy('id')->pluck('id', 'email');

        $orders = [
            ['customer_id' => $customers['ahmet@example.com'], 'order_number' => 'ORD-1001', 'total_amount' => 1250.00, 'status' => 'completed', 'notes' => 'Kapıda ödeme seçildi.'],
            ['customer_id' => $customers['ahmet@example.com'], 'order_number' => 'ORD-1002', 'total_amount' => 450.50, 'status' => 'processing', 'notes' => 'Hızlı kargo talep edildi.'],
            ['customer_id' => $customers['ayse@example.com'], 'order_number' => 'ORD-1003', 'total_amount' => 3200.00, 'status' => 'pending', 'notes' => 'Havale bekleniyor.'],
            ['customer_id' => $customers['mehmet@example.com'], 'order_number' => 'ORD-1004', 'total_amount' => 890.00, 'status' => 'completed', 'notes' => 'Hediye paketi yapıldı.'],
        ];

        foreach ($orders as $order) {
            Order::create($order);
        }

        $customerIds = $customers->values();

        Order::factory()
            ->count(100 - count($orders))
            ->sequence(fn ($sequence) => [
                'customer_id' => $customerIds->random(),
                'order_number' => 'ORD-'.(1001 + count($orders) + $sequence->index),
            ])
            ->create();
    }
}
