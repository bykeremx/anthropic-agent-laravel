<?php

namespace Database\Seeders;

use App\Models\Customer;
use Illuminate\Database\Seeder;

class CustomerSeeder extends Seeder
{
    /**
     * 30 müşteri: db-schema.md'deki 3 örnek müşteri + 27 rastgele müşteri.
     */
    public function run(): void
    {
        $customers = [
            ['name' => 'Ahmet Yılmaz', 'email' => 'ahmet@example.com', 'phone' => '5551112233', 'city' => 'İstanbul'],
            ['name' => 'Ayşe Demir', 'email' => 'ayse@example.com', 'phone' => '5554445566', 'city' => 'Ankara'],
            ['name' => 'Mehmet Kaya', 'email' => 'mehmet@example.com', 'phone' => '5557778899', 'city' => 'İzmir'],
        ];

        foreach ($customers as $customer) {
            Customer::create($customer);
        }

        Customer::factory()->count(30 - count($customers))->create();
    }
}
