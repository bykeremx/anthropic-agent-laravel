<?php

namespace App\Services\Ai;

use Illuminate\Support\Facades\Http;

class AiClient {
    public function send(array $messages , string $system = "" ,  array $tools = []):array{

        $payload  = [
            'model' => config('services.anthropic.model'),
            'messages' => $messages, // dizi olacak ve içeriği role ve content olacak şekilde
            'max_tokens' => 1024,
        ];

        if ($system !== '') {
            $payload['system'] = $system;
        }
        if (!empty($tools)) {
            $payload['tools'] = $tools;
        }

        return Http::withHeaders([
            'x-api-key' => config('services.anthropic.key'),
            "anthropic-version" => "2023-06-01"
        ])
        ->timeout(30)
        ->post('https://api.anthropic.com/v1/messages', $payload
        )->throw()->json();
    }
}
