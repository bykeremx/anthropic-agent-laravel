<?php

use App\Models\Customer;
use App\Models\Order;
use App\Services\Ai\AiAgent;
use Illuminate\Support\Facades\Http;

beforeEach(function () {
    config([
        'services.anthropic.key' => 'test-key',
        'services.anthropic.model' => 'test-model',
    ]);
});

describe('run', function () {
    it('returns the first response unchanged when the model does not request a tool', function () {
        $final = anthropicResponse('end_turn', [anthropicTextBlock('Merhaba, nasıl yardımcı olabilirim?')]);
        Http::fake([ANTHROPIC_MESSAGES_URL => Http::response($final)]);

        $response = app(AiAgent::class)->run([['role' => 'user', 'content' => 'Merhaba']]);

        expect($response)->toBe($final);
        Http::assertSentCount(1);
    });

    it('sends the system prompt and both tool definitions with the request', function () {
        Http::fake([ANTHROPIC_MESSAGES_URL => Http::response(anthropicResponse('end_turn', []))]);

        app(AiAgent::class)->run([['role' => 'user', 'content' => 'Merhaba']]);

        $request = Http::recorded()->first()[0];
        expect($request['system'])->toBeString()->not->toBeEmpty();
        expect(array_column($request['tools'], 'name'))->toBe(['get_customer_orders', 'get_order_status']);
    });

    it('feeds the tool result back to the model under the matching tool_use id', function () {
        Order::factory()
            ->for(Customer::factory()->state(['name' => 'Ayşe Demir']))
            ->create(['order_number' => 'ORD-1003', 'status' => 'processing']);
        $toolTurn = anthropicResponse('tool_use', [
            anthropicTextBlock('Siparişe bakıyorum.'),
            anthropicToolUseBlock('toolu_1', 'get_order_status', ['order_number' => 'ORD-1003']),
        ]);
        Http::fake([
            ANTHROPIC_MESSAGES_URL => Http::sequence()
                ->push($toolTurn)
                ->push(anthropicResponse('end_turn', [anthropicTextBlock('Hazırlanıyor.')])),
        ]);

        app(AiAgent::class)->run([['role' => 'user', 'content' => 'ORD-1003 ne durumda?']]);

        $messages = Http::recorded()[1][0]['messages'];
        expect($messages)->toHaveCount(3);
        expect($messages[1])->toBe(['role' => 'assistant', 'content' => $toolTurn['content']]);
        expect($messages[2]['role'])->toBe('user');
        expect($messages[2]['content'])->toHaveCount(1);
        expect($messages[2]['content'][0])
            ->toMatchArray(['type' => 'tool_result', 'tool_use_id' => 'toolu_1', 'is_error' => false]);
        expect($messages[2]['content'][0]['content'])
            ->toContain('Ayşe Demir')
            ->json()
            ->status->toBe('success')
            ->order->order_status->toBe('processing');
    });

    it('returns the results of parallel tool calls in a single user message', function () {
        Http::fake([
            ANTHROPIC_MESSAGES_URL => Http::sequence()
                ->push(anthropicResponse('tool_use', [
                    anthropicToolUseBlock('toolu_1', 'get_order_status', ['order_number' => 'ORD-1']),
                    anthropicToolUseBlock('toolu_2', 'get_customer_orders', ['customer_name' => 'Ahmet']),
                ]))
                ->push(anthropicResponse('end_turn', [anthropicTextBlock('Bulunamadı.')])),
        ]);

        app(AiAgent::class)->run([['role' => 'user', 'content' => 'ORD-1 ve Ahmet?']]);

        $messages = Http::recorded()[1][0]['messages'];
        expect($messages)->toHaveCount(3);
        expect(array_column($messages[2]['content'], 'tool_use_id'))->toBe(['toolu_1', 'toolu_2']);
    });

    it('marks the tool result as an error when the model requests an unknown tool', function () {
        Http::fake([
            ANTHROPIC_MESSAGES_URL => Http::sequence()
                ->push(anthropicResponse('tool_use', [
                    anthropicToolUseBlock('toolu_1', 'delete_customer', ['id' => 1]),
                ]))
                ->push(anthropicResponse('end_turn', [anthropicTextBlock('Bunu yapamam.')])),
        ]);

        app(AiAgent::class)->run([['role' => 'user', 'content' => 'Müşteriyi sil']]);

        $toolResult = Http::recorded()[1][0]['messages'][2]['content'][0];
        expect($toolResult['is_error'])->toBeTrue();
        expect($toolResult['content'])->json()->message->toBe('Bilinmeyen tool: delete_customer');
    });

    it('stops after five requests and returns the step limit message', function () {
        Http::fake([
            ANTHROPIC_MESSAGES_URL => Http::response(anthropicResponse('tool_use', [
                anthropicToolUseBlock('toolu_1', 'get_order_status', ['order_number' => 'ORD-1']),
            ])),
        ]);

        $response = app(AiAgent::class)->run([['role' => 'user', 'content' => 'ORD-1?']]);

        expect($response)->toBe([
            'stop_reason' => 'max_steps',
            'content' => [
                anthropicTextBlock('Bu soruyu yanıtlamak için çok fazla adım gerekti. Lütfen soruyu daha net sorar mısın?'),
            ],
        ]);
        Http::assertSentCount(5);
    });
});

describe('text', function () {
    it('joins every text block of a response with a newline', function () {
        $response = anthropicResponse('end_turn', [
            anthropicTextBlock('Birinci'),
            anthropicToolUseBlock('toolu_1', 'get_order_status', ['order_number' => 'ORD-1']),
            anthropicTextBlock('İkinci'),
        ]);

        expect(AiAgent::text($response))->toBe("Birinci\nİkinci");
    });

    it('returns an empty string when the response has no text block', function () {
        expect(AiAgent::text(['stop_reason' => 'end_turn']))->toBe('');
    });
});
