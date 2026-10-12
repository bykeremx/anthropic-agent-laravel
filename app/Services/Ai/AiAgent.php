<?php

namespace App\Services\Ai;

use App\Schema\ToolSchema;

class AiAgent {

    private string $system = 'Sen bir e-ticaret mağazasının müşteri hizmetleri asistanısın. ' .
        'Müşteri ve sipariş bilgilerini yalnızca sana verilen tool\'larla öğren; tool sonucunda olmayan bir bilgiyi asla uydurma. ' .
        'Bir kayıt bulunamazsa bunu açıkça söyle. Birden fazla müşteri eşleşirse hangisini kastettiğini sor ya da hepsini kısaca listele. ' .
        'Sipariş durumlarını Türkçe ifade et: pending = beklemede, processing = hazırlanıyor, completed = tamamlandı, cancelled = iptal edildi. ' .
        'Tutarları TL olarak yaz. Her zaman Türkçe, kısa ve net cevap ver.';

    private array $tools;

    private int $maxSteps = 5;

    public function __construct(
        private AiClient $aiClient,
        private ToolsService $toolsService,
    )
    {
        $this->tools = ToolSchema::all();
    }

    /**
     * Agent döngüsünü çalıştırır ve son Anthropic yanıtını döndürür.
     */
    public function run(array $messages): array
    {
        for ($step = 0; $step < $this->maxSteps; $step++) {
            $response = $this->aiClient->send($messages, $this->system, $this->tools);

            if (($response['stop_reason'] ?? null) !== 'tool_use') {
                return $response;
            }

            // Modelin yanıtı (tool_use blokları dahil) olduğu gibi geçmişe eklenir.
            $messages[] = [
                'role' => 'assistant',
                'content' => $response['content'],
            ];

            // Her tool_use bloğu çalıştırılır, sonuçlar tek bir user mesajıyla geri gönderilir.
            $toolResults = [];

            foreach ($response['content'] as $block) {
                if (($block['type'] ?? null) !== 'tool_use') {
                    continue;
                }

                $result = $this->toolsService->call($block['name'], (array) ($block['input'] ?? []));

                $toolResults[] = [
                    'type' => 'tool_result',
                    'tool_use_id' => $block['id'],
                    'content' => json_encode($result, JSON_UNESCAPED_UNICODE),
                    'is_error' => ($result['status'] ?? null) === 'error',
                ];
            }

            $messages[] = [
                'role' => 'user',
                'content' => $toolResults,
            ];
        }

        return [
            'stop_reason' => 'max_steps',
            'content' => [
                ['type' => 'text', 'text' => 'Bu soruyu yanıtlamak için çok fazla adım gerekti. Lütfen soruyu daha net sorar mısın?'],
            ],
        ];
    }

    /**
     * Anthropic yanıtındaki metin bloklarını birleştirir.
     */
    public static function text(array $response): string
    {
        return collect($response['content'] ?? [])
            ->where('type', 'text')
            ->pluck('text')
            ->implode("\n");
    }
}
