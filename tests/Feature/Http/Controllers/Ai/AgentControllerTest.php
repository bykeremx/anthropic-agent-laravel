<?php

use App\Models\Customer;
use App\Models\Order;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

beforeEach(function () {
    config([
        'services.anthropic.key' => 'test-key',
        'services.anthropic.model' => 'test-model',
    ]);
});

describe('index', function () {
    it('renders the chat page wired to the send endpoint', function () {
        $response = $this->get(route('ai.agent'));

        $response->assertOk()
            ->assertViewIs('ai.agent')
            ->assertSee('data-endpoint="'.route('ai.send').'"', false);
    });
});

describe('post', function () {
    it('rejects a request without a message with 422', function () {
        Http::fake([ANTHROPIC_MESSAGES_URL => Http::response(anthropicResponse('end_turn', []))]);

        $response = $this->postJson(route('ai.send'), []);

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['message' => 'The message field is required.']);
        Http::assertNothingSent();
    });

    it('rejects an invalid message with 422', function (mixed $message, string $error) {
        Http::fake([ANTHROPIC_MESSAGES_URL => Http::response(anthropicResponse('end_turn', []))]);

        $response = $this->postJson(route('ai.send'), ['message' => $message]);

        $response->assertUnprocessable()
            ->assertJsonValidationErrors(['message' => $error]);
        Http::assertNothingSent();
    })->with([
        'not a string' => [['ORD-1001'], 'The message field must be a string.'],
        'longer than 2000 characters' => [str_repeat('a', 2001), 'The message field must not be greater than 2000 characters.'],
    ]);

    it('returns the model reply after running the requested tool', function () {
        Order::factory()
            ->for(Customer::factory()->state(['name' => 'Ayşe Demir']))
            ->create(['order_number' => 'ORD-1003', 'status' => 'processing']);
        Http::fake([
            ANTHROPIC_MESSAGES_URL => Http::sequence()
                ->push(anthropicResponse('tool_use', [
                    anthropicToolUseBlock('toolu_1', 'get_order_status', ['order_number' => 'ORD-1003']),
                ]))
                ->push(anthropicResponse('end_turn', [
                    anthropicTextBlock('ORD-1003 numaralı sipariş hazırlanıyor.'),
                ])),
        ]);

        $response = $this->postJson(route('ai.send'), ['message' => 'ORD-1003 siparişinin durumu ne?']);

        $response->assertOk()
            ->assertExactJson(['reply' => 'ORD-1003 numaralı sipariş hazırlanıyor.']);
        Http::assertSentCount(2);
    });

    it('falls back to a default reply when the model returns no text', function () {
        Http::fake([ANTHROPIC_MESSAGES_URL => Http::response(anthropicResponse('max_tokens', []))]);

        $response = $this->postJson(route('ai.send'), ['message' => 'Merhaba']);

        $response->assertOk()
            ->assertExactJson(['reply' => 'Bir cevap üretilemedi.']);
    });

    it('returns 502 and logs the API error when Anthropic responds with an error', function () {
        Log::spy();
        $errorBody = ['type' => 'error', 'error' => ['type' => 'overloaded_error', 'message' => 'Overloaded']];
        Http::fake([ANTHROPIC_MESSAGES_URL => Http::response($errorBody, 529)]);

        $response = $this->postJson(route('ai.send'), ['message' => 'Merhaba']);

        $response->assertStatus(502)
            ->assertExactJson(['message' => 'AI servisine ulaşılamadı. Lütfen tekrar dene.']);
        Log::shouldHaveReceived('error')
            ->with('Anthropic API hatası', ['status' => 529, 'body' => $errorBody])
            ->once();
    });

    it('returns 500 when the connection to Anthropic fails', function () {
        Http::fake([ANTHROPIC_MESSAGES_URL => Http::failedConnection()]);

        $response = $this->postJson(route('ai.send'), ['message' => 'Merhaba']);

        $response->assertInternalServerError()
            ->assertExactJson(['message' => 'Beklenmeyen bir hata oluştu.']);
    });
});
