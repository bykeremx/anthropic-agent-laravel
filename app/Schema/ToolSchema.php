<?php
namespace App\Schema;

class ToolSchema
{
    /**
     * Anthropic Messages API tool şemaları.
     */
    public static function all(): array
    {
        return [
            [
                'name' => 'get_customer_orders',
                'description' => 'Veritabanında kayıtlı bir müşterinin sipariş geçmişini listeler: sipariş numarası, durum, tutar, not ve tarih. ' .
                                 'Kullanıcı bir müşterinin siparişlerini, sipariş durumlarını veya toplam harcamasını sorduğunda bu aracı kullanın. ' .
                                 'Müşteri adı veya soyadıyla arama yapar ve birden fazla müşteri eşleşebilir (en fazla 5). ' .
                                 'Sipariş numarası ile arama yapmak için bu araç yerine `get_order_status` kullanın.',
                'input_schema' => [
                    'type' => 'object',
                    'properties' => [
                        'customer_name' => [
                            'type' => 'string',
                            'description' => 'Sorgulanacak müşterinin adı, soyadı veya ikisi birden (Örn: Ahmet Yılmaz, Mehmet)'
                        ]
                    ],
                    'required' => ['customer_name']
                ],
            ],
            [
                'name' => 'get_order_status',
                'description' => 'Sipariş numarası vererek tek bir siparişin durumunu (pending, processing, completed, cancelled), tutarını, notunu, tarihini ve müşterisini getirir. ' .
                                 'Kullanıcı elindeki belirli bir sipariş numarasını sorduğunda bu aracı kullanın. ' .
                                 'Müşterinin tüm siparişlerini görmek için bu aracı değil `get_customer_orders` kullanın.',
                'input_schema' => [
                    'type' => 'object',
                    'properties' => [
                        'order_number' => [
                            'type' => 'string',
                            'description' => 'Sipariş numarası, "ORD-" önekiyle (Örn: ORD-1001)'
                        ]
                    ],
                    'required' => ['order_number']
                ],
            ],
        ];
    }
}
