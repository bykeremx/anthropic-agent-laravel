<?php

use App\Schema\ToolSchema;
use App\Services\Ai\ToolsService;

dataset('declared tools', function () {
    foreach (ToolSchema::all() as $tool) {
        yield $tool['name'] => [$tool];
    }
});

it('maps every declared tool to a public ToolsService method of the same name', function (array $tool) {
    $method = new ReflectionMethod(ToolsService::class, $tool['name']);

    expect($method->isPublic())->toBeTrue();
})->with('declared tools');

it('declares every required input as a schema property', function (array $tool) {
    expect($tool['input_schema']['properties'])->toHaveKeys($tool['input_schema']['required']);
})->with('declared tools');
