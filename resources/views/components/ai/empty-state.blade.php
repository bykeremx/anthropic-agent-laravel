@props([
    'title' => 'Bugün sana nasıl yardımcı olabilirim?',
    'suggestions' => [],
])

<div {{ $attributes->class('mx-auto flex max-w-2xl flex-col items-center px-4 py-12 text-center sm:py-20') }} data-empty-state>
    <x-ai.avatar role="assistant" class="size-12" />

    <h2 class="mt-5 text-xl font-semibold tracking-tight sm:text-2xl">{{ $title }}</h2>
    <p class="mt-2 text-sm text-zinc-500">Aşağıdan bir örnek seç ya da kendi sorunu yaz.</p>

    @if (count($suggestions))
        <div class="mt-8 grid w-full gap-3 sm:grid-cols-2">
            @foreach ($suggestions as $suggestion)
                <x-ai.suggestion :prompt="$suggestion" />
            @endforeach
        </div>
    @endif
</div>
