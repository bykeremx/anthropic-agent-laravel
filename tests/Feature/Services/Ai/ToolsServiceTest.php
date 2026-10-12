<?php

use App\Models\Customer;
use App\Models\Order;
use App\Services\Ai\ToolsService;

describe('get_customer_orders', function () {
    it('returns partially matching customers with their orders newest first', function () {
        $ahmet = Customer::factory()->create(['name' => 'Ahmet Yılmaz', 'email' => 'ahmet@example.com', 'city' => 'İzmir']);
        Customer::factory()->create(['name' => 'Ayşe Demir']);
        Order::factory()->for($ahmet)->create([
            'order_number' => 'ORD-2001', 'status' => 'completed', 'total_amount' => 150.25,
            'notes' => null, 'created_at' => '2026-01-10 09:00:00',
        ]);
        Order::factory()->for($ahmet)->create([
            'order_number' => 'ORD-2002', 'status' => 'pending', 'total_amount' => 80,
            'notes' => 'Hızlı kargo talep edildi.', 'created_at' => '2026-03-05 14:30:00',
        ]);

        $result = app(ToolsService::class)->call('get_customer_orders', ['customer_name' => 'Ahmet']);

        expect($result)->toBe([
            'status' => 'success',
            'match_count' => 1,
            'customers' => [[
                'name' => 'Ahmet Yılmaz',
                'email' => 'ahmet@example.com',
                'city' => 'İzmir',
                'order_count' => 2,
                'total_spent' => 230.25,
                'orders' => [
                    [
                        'order_number' => 'ORD-2002',
                        'order_status' => 'pending',
                        'total_amount' => 80.0,
                        'notes' => 'Hızlı kargo talep edildi.',
                        'created_at' => '2026-03-05',
                    ],
                    [
                        'order_number' => 'ORD-2001',
                        'order_status' => 'completed',
                        'total_amount' => 150.25,
                        'notes' => null,
                        'created_at' => '2026-01-10',
                    ],
                ],
            ]],
        ]);
    });

    it('excludes cancelled orders from the total spent', function () {
        $customer = Customer::factory()->create(['name' => 'Zeynep Kaya']);
        Order::factory()->for($customer)->count(3)->sequence(
            ['status' => 'completed', 'total_amount' => 100.50],
            ['status' => 'pending', 'total_amount' => 200],
            ['status' => 'cancelled', 'total_amount' => 999],
        )->create();

        $result = app(ToolsService::class)->call('get_customer_orders', ['customer_name' => 'Zeynep Kaya']);

        expect($result['customers'][0])
            ->order_count->toBe(3)
            ->total_spent->toBe(300.5);
    });

    it('returns at most five matching customers', function () {
        Customer::factory()->count(6)->sequence(fn ($sequence) => ['name' => "Mehmet {$sequence->index}"])->create();

        $result = app(ToolsService::class)->call('get_customer_orders', ['customer_name' => 'Mehmet']);

        expect($result['match_count'])->toBe(5);
        expect($result['customers'])->toHaveCount(5);
    });

    it('returns an error when the customer name is blank', function (array $input) {
        Customer::factory()->create();

        $result = app(ToolsService::class)->call('get_customer_orders', $input);

        expect($result)->toBe(['status' => 'error', 'message' => 'Müşteri adı boş olamaz.']);
    })->with([
        'missing' => [[]],
        'empty' => [['customer_name' => '']],
        'whitespace only' => [['customer_name' => '   ']],
    ]);

    it('returns an error when no customer matches', function () {
        Customer::factory()->create(['name' => 'Ayşe Demir']);

        $result = app(ToolsService::class)->call('get_customer_orders', ['customer_name' => 'Burak']);

        expect($result)->toBe(['status' => 'error', 'message' => 'Müşteri bulunamadı.']);
    });
});

describe('get_order_status', function () {
    it('returns the order together with its customer name', function () {
        Order::factory()
            ->for(Customer::factory()->state(['name' => 'Ayşe Demir']))
            ->create([
                'order_number' => 'ORD-1003', 'status' => 'processing', 'total_amount' => 1249.90,
                'notes' => 'Hediye paketi yapıldı.', 'created_at' => '2026-10-05 11:15:00',
            ]);

        $result = app(ToolsService::class)->call('get_order_status', ['order_number' => 'ORD-1003']);

        expect($result)->toBe([
            'status' => 'success',
            'order' => [
                'order_number' => 'ORD-1003',
                'order_status' => 'processing',
                'total_amount' => 1249.9,
                'notes' => 'Hediye paketi yapıldı.',
                'created_at' => '2026-10-05',
                'customer' => 'Ayşe Demir',
            ],
        ]);
    });

    it('finds the order when the number is given in another format', function (string $orderNumber) {
        Order::factory()->create(['order_number' => 'ORD-2001']);

        $result = app(ToolsService::class)->call('get_order_status', ['order_number' => $orderNumber]);

        expect($result['order']['order_number'])->toBe('ORD-2001');
    })->with([
        'digits only' => ['2001'],
        'lowercase prefix' => ['ord-2001'],
        'surrounding whitespace' => ['  ORD-2001 '],
    ]);

    it('returns an error naming the order number when the order does not exist', function () {
        Order::factory()->create(['order_number' => 'ORD-2001']);

        $result = app(ToolsService::class)->call('get_order_status', ['order_number' => '9999']);

        expect($result)->toBe(['status' => 'error', 'message' => 'ORD-9999 numaralı sipariş bulunamadı.']);
    });
});

describe('call', function () {
    it('refuses to run a method that is not declared as a tool', function (string $name) {
        $result = app(ToolsService::class)->call($name, []);

        expect($result)->toBe(['status' => 'error', 'message' => "Bilinmeyen tool: {$name}"]);
    })->with([
        'private helper' => ['formatOrder'],
        'dispatcher itself' => ['call'],
        'undeclared tool' => ['delete_customer'],
    ]);
});
