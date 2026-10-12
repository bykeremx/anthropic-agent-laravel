@props(['prompt'])

<button
    type="button"
    data-suggestion="{{ $prompt }}"
    {{ $attributes->class('rounded-xl border border-zinc-200 bg-white px-4 py-3 text-left text-sm text-zinc-700 shadow-sm transition hover:border-indigo-300 hover:bg-indigo-50/50 hover:text-zinc-900') }}
>
    {{ $slot->isEmpty() ? $prompt : $slot }}
</button>
