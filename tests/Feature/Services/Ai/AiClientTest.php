<?php

use App\Services\Ai\AiClient;
use Illuminate\Http\Client\RequestException;
use Illuminate\Support\Facades\Http;

beforeEach(function () {
    config([
        'services.anthropic.key' => 'test-key',
        'services.anthropic.model' => 'test-model',
    ]);
});

it('posts the conversation with the configured key, model and API version', function () {
    Http::fake([ANTHROPIC_MESSAGES_URL => Http::response(anthropicResponse('end_turn', []))]);
    $messages = [['role' => 'user', 'content' => 'Merhaba']];
    $tools = [['name' => 'get_order_status', 'description' => 'Sipariş durumu', 'input_schema' => ['type' => 'object']]];

    app(AiClient::class)->send($messages, 'Sistem talimatı', $tools);

    $request = Http::recorded()->first()[0];
    expect($request->method())->toBe('POST');
    expect($request->header('x-api-key'))->toBe(['test-key']);
    expect($request->header('anthropic-version'))->toBe(['2023-06-01']);
    expect($request->data())->toBe([
        'model' => 'test-model',
        'messages' => $messages,
        'max_tokens' => 1024,
        'system' => 'Sistem talimatı',
        'tools' => $tools,
    ]);
});

it('omits the system prompt and tools when none are given', function () {
    Http::fake([ANTHROPIC_MESSAGES_URL => Http::response(anthropicResponse('end_turn', []))]);

    app(AiClient::class)->send([['role' => 'user', 'content' => 'Merhaba']]);

    expect(Http::recorded()->first()[0]->data())
        ->not->toHaveKey('system')
        ->not->toHaveKey('tools');
});

it('returns the decoded response body', function () {
    $body = anthropicResponse('end_turn', [anthropicTextBlock('Merhaba!')]);
    Http::fake([ANTHROPIC_MESSAGES_URL => Http::response($body)]);

    $response = app(AiClient::class)->send([['role' => 'user', 'content' => 'Merhaba']]);

    expect($response)->toBe($body);
});

it('throws a request exception when the API responds with an error status', function () {
    Http::fake([
        ANTHROPIC_MESSAGES_URL => Http::response(
            ['type' => 'error', 'error' => ['type' => 'authentication_error', 'message' => 'invalid x-api-key']],
            401,
        ),
    ]);

    $send = fn () => app(AiClient::class)->send([['role' => 'user', 'content' => 'Merhaba']]);

    expect($send)->toThrow(RequestException::class);
});
