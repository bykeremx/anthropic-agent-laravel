<?php

use Illuminate\Foundation\Testing\LazilyRefreshDatabase;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

/*
|--------------------------------------------------------------------------
| Test Case
|--------------------------------------------------------------------------
|
| The closure you provide to your test functions is always bound to a specific PHPUnit test
| case class. By default, that class is "PHPUnit\Framework\TestCase". Of course, you may
| need to change it using the "pest()" function to bind different classes or traits.
|
*/

pest()->extend(TestCase::class)
    ->use(LazilyRefreshDatabase::class)
    ->beforeEach(function () {
        Http::preventStrayRequests();
        $this->withoutVite();
    })
    ->in('Feature');

/*
|--------------------------------------------------------------------------
| Expectations
|--------------------------------------------------------------------------
|
| When you're writing tests, you often need to check that values meet certain conditions. The
| "expect()" function gives you access to a set of "expectations" methods that you can use
| to assert different things. Of course, you may extend the Expectation API at any time.
|
*/

expect()->extend('toBeOne', function () {
    return $this->toBe(1);
});

/*
|--------------------------------------------------------------------------
| Functions
|--------------------------------------------------------------------------
|
| While Pest is very powerful out-of-the-box, you may have some testing code specific to your
| project that you don't want to repeat in every file. Here you can also expose helpers as
| global functions to help you to reduce the number of lines of code in your test files.
|
*/

function something()
{
    // ..
}

const ANTHROPIC_MESSAGES_URL = 'https://api.anthropic.com/v1/messages';

/**
 * Builds a Messages API response body as returned by Anthropic.
 *
 * @param  array<int, array<string, mixed>>  $content
 * @return array{id: string, type: string, role: string, stop_reason: string, content: array<int, array<string, mixed>>}
 */
function anthropicResponse(string $stopReason, array $content): array
{
    return [
        'id' => 'msg_test',
        'type' => 'message',
        'role' => 'assistant',
        'stop_reason' => $stopReason,
        'content' => $content,
    ];
}

/**
 * @return array{type: string, text: string}
 */
function anthropicTextBlock(string $text): array
{
    return ['type' => 'text', 'text' => $text];
}

/**
 * @param  array<string, mixed>  $input
 * @return array{type: string, id: string, name: string, input: array<string, mixed>}
 */
function anthropicToolUseBlock(string $id, string $name, array $input): array
{
    return ['type' => 'tool_use', 'id' => $id, 'name' => $name, 'input' => $input];
}
