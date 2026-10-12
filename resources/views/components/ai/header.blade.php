@props([
    'title' => 'AI Asistan',
    'subtitle' => 'Sorunu yaz, cevabı anında al.',
])

<header {{ $attributes->class('flex items-center justify-between gap-4 border-b border-zinc-200 bg-white/80 px-4 py-3 backdrop-blur sm:px-6') }}>
    <div class="flex items-center gap-3">
        <x-ai.avatar role="assistant" />
        <div>
            <h1 class="text-sm font-semibold leading-tight">{{ $title }}</h1>
            <p class="text-xs text-zinc-500">{{ $subtitle }}</p>
        </div>
    </div>

    <div class="flex items-center gap-2">
        {{ $slot }}
    </div>
</header>
