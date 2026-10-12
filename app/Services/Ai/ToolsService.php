<?php

namespace App\Services\Ai;

use App\Models\Customer;
use App\Models\Order;
use App\Schema\ToolSchema;

class ToolsService
{
    /**
     * Modelin istediği tool'u çalıştırır. Sadece ToolSchema'da tanımlı tool'lar çağrılabilir.
     */
    public function call(string $name, array $input): array
    {
        $allowed = array_column(ToolSchema::all(), 'name');

        if (! in_array($name, $allowed, true) || ! method_exists($this, $name)) {
            return ['status' => 'error', 'message' => "Bilinmeyen tool: {$name}"];
        }

        return $this->{$name}($input);
    }

    /**
     * Tool adı: get_customer_orders
     */
    public function get_customer_orders(array $input): array
    {
        $customerName = trim((string) ($input['customer_name'] ?? ''));

        if ($customerName === '') {
            return ['status' => 'error', 'message' => 'Müşteri adı boş olamaz.'];
        }

        $customers = Customer::where('name', 'like', "%{$customerName}%")
            ->with(['orders' => fn ($query) => $query->latest()])
            ->limit(5)
            ->get();

        if ($customers->isEmpty()) {
            return ['status' => 'error', 'message' => 'Müşteri bulunamadı.'];
        }

        return [
            'status' => 'success',
            'match_count' => $customers->count(),
            'customers' => $customers->map(fn (Customer $customer) => [
                'name' => $customer->name,
                'email' => $customer->email,
                'city' => $customer->city,
                'order_count' => $customer->orders->count(),
                'total_spent' => (float) $customer->orders->where('status', '!=', 'cancelled')->sum('total_amount'),
                'orders' => $customer->orders->map(fn (Order $order) => $this->formatOrder($order))->all(),
            ])->all(),
        ];
    }

    /**
     * Tool adı: get_order_status
     */
    public function get_order_status(array $input): array
    {
        $orderNumber = strtoupper(trim((string) ($input['order_number'] ?? '')));

        // "1001" gibi sadece rakam gelirse "ORD-1001" olarak ara.
        if (ctype_digit($orderNumber)) {
            $orderNumber = "ORD-{$orderNumber}";
        }

        $order = Order::with('customer')->where('order_number', $orderNumber)->first();

        if (! $order) {
            return ['status' => 'error', 'message' => "{$orderNumber} numaralı sipariş bulunamadı."];
        }

        return [
            'status' => 'success',
            'order' => $this->formatOrder($order) + ['customer' => $order->customer->name],
        ];
    }

    private function formatOrder(Order $order): array
    {
        return [
            'order_number' => $order->order_number,
            'order_status' => $order->status,
            'total_amount' => (float) $order->total_amount,
            'notes' => $order->notes,
            'created_at' => $order->created_at?->toDateString(),
        ];
    }
}
