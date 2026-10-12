@props([
    'placeholder' => 'Bir soru sor…',
])

<div {{ $attributes->class('border-t border-zinc-200 bg-white/80 px-4 py-4 backdrop-blur sm:px-6') }}>
    <form class="mx-auto flex max-w-3xl items-end gap-2" data-ai-form>
        <label for="ai-prompt" class="sr-only">Soru</label>
        <textarea
            id="ai-prompt"
            name="prompt"
            rows="1"
            placeholder="{{ $placeholder }}"
            class="max-h-48 min-h-11 flex-1 resize-none rounded-xl border border-zinc-300 bg-white px-4 py-2.5 text-sm shadow-sm outline-none transition placeholder:text-zinc-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            data-ai-input
        ></textarea>

        <button
            type="submit"
            class="inline-flex size-11 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm transition hover:bg-indigo-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Gönder"
            data-ai-submit
        >
            <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M5 12h14" /><path d="M13 6l6 6-6 6" />
            </svg>
        </button>
    </form>

    <p class="mx-auto mt-2 max-w-3xl text-center text-[11px] text-zinc-400">
        Göndermek için <kbd class="font-sans font-semibold">Enter</kbd>, yeni satır için <kbd class="font-sans font-semibold">Shift + Enter</kbd>.
    </p>
</div>
