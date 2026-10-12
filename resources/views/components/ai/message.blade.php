@props([
    'role' => 'assistant', // user | assistant | error
    'content' => null,
])

@php
    $isUser = $role === 'user';
    $bubble = match ($role) {
        'user' => 'bg-zinc-900 text-white rounded-br-md',
        'error' => 'bg-red-50 text-red-700 ring-1 ring-red-200 rounded-bl-md',
        default => 'bg-white text-zinc-800 ring-1 ring-zinc-200 rounded-bl-md',
    };
@endphp

<div {{ $attributes->class(['flex items-end gap-3', 'flex-row-reverse' => $isUser]) }} data-role="{{ $role }}">
    <x-ai.avatar :role="$isUser ? 'user' : 'assistant'" />

    <div class="max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm sm:max-w-[75%] {{ $bubble }}">
        <div class="whitespace-pre-wrap break-words" data-content>{{ $content ?? $slot }}</div>
    </div>
</div>
