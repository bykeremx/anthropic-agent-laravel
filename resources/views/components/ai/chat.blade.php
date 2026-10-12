@props([
    'endpoint' => null, // POST {message: string} (geçmiş tutulmaz) → {reply} | Anthropic yanıtı
    'title' => 'AI Asistan',
    'subtitle' => 'Sorunu yaz, cevabı anında al.',
    'placeholder' => 'Bir soru sor…',
    'suggestions' => [],
])

<div {{ $attributes->class('flex h-dvh flex-col') }} data-ai-chat data-endpoint="{{ $endpoint }}">
    <x-ai.header :title="$title" :subtitle="$subtitle">
        <button
            type="button"
            class="rounded-lg px-3 py-1.5 text-xs font-medium text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900"
            data-ai-reset
        >
            Yeni sohbet
        </button>
    </x-ai.header>

    <main class="flex-1 overflow-y-auto" data-ai-scroll>
        <x-ai.empty-state :suggestions="$suggestions" />

        <div class="mx-auto hidden max-w-3xl flex-col gap-5 px-4 py-6 sm:px-6" data-ai-messages></div>
    </main>

    <x-ai.prompt-input :placeholder="$placeholder" />

    <template data-ai-template="user"><x-ai.message role="user" /></template>
    <template data-ai-template="assistant"><x-ai.message role="assistant" /></template>
    <template data-ai-template="error"><x-ai.message role="error" /></template>
    <template data-ai-template="typing"><x-ai.typing /></template>
</div>

@once
    @push('scripts')
        <script>
            document.querySelectorAll('[data-ai-chat]').forEach((root) => {
                const endpoint = root.dataset.endpoint;
                const form = root.querySelector('[data-ai-form]');
                const input = root.querySelector('[data-ai-input]');
                const submit = root.querySelector('[data-ai-submit]');
                const list = root.querySelector('[data-ai-messages]');
                const scroller = root.querySelector('[data-ai-scroll]');
                const emptyState = root.querySelector('[data-empty-state]');
                const csrf = document.querySelector('meta[name="csrf-token"]')?.content;

                let busy = false;

                const render = (name, text = '') => {
                    const node = root.querySelector(`[data-ai-template="${name}"]`).content.firstElementChild.cloneNode(true);
                    const content = node.querySelector('[data-content]');
                    if (content) content.textContent = text;
                    list.appendChild(node);
                    scroller.scrollTo({ top: scroller.scrollHeight, behavior: 'smooth' });
                    return node;
                };

                const toggleEmpty = (empty) => {
                    emptyState.classList.toggle('hidden', !empty);
                    list.classList.toggle('hidden', empty);
                    list.classList.toggle('flex', !empty);
                };

                const autosize = () => {
                    input.style.height = 'auto';
                    input.style.height = `${input.scrollHeight}px`;
                };

                const setBusy = (state) => {
                    busy = state;
                    submit.disabled = state;
                };

                const extractReply = (data) => {
                    if (typeof data?.reply === 'string') return data.reply;
                    if (Array.isArray(data?.content)) {
                        return data.content.filter((b) => b.type === 'text').map((b) => b.text).join('\n');
                    }
                    return typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                };

                const ask = async (text) => {
                    if (busy || !text.trim()) return;
                    toggleEmpty(false);
                    render('user', text);
                    input.value = '';
                    autosize();
                    setBusy(true);
                    const typing = render('typing');
                    try {
                        if (!endpoint) {
                            await new Promise((r) => setTimeout(r, 700));
                            throw new Error('Henüz bir endpoint bağlı değil. Bileşene endpoint="..." ile bir adres ver.');
                        }
                        const res = await fetch(endpoint, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json',
                                'X-CSRF-TOKEN': csrf,
                            },
                            body: JSON.stringify({ message: text }),
                        });
                        if (!res.ok) {
                            const error = await res.json().catch(() => ({}));
                            throw new Error(error.message || `İstek başarısız oldu (${res.status}).`);
                        }
                        const reply = extractReply(await res.json());
                        typing.remove();
                        render('assistant', reply);
                    } catch (e) {
                        typing.remove();
                        render('error', e.message || 'Bir hata oluştu.');
                    } finally {
                        setBusy(false);
                        input.focus();
                    }
                };

                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    ask(input.value);
                });

                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
                        e.preventDefault();
                        form.requestSubmit();
                    }
                });

                input.addEventListener('input', autosize);

                root.querySelectorAll('[data-suggestion]').forEach((btn) => {
                    btn.addEventListener('click', () => ask(btn.dataset.suggestion));
                });

                root.querySelector('[data-ai-reset]').addEventListener('click', () => {
                    if (busy) return;
                    list.innerHTML = '';
                    toggleEmpty(true);
                    input.focus();
                });
            });
        </script>
    @endpush
@endonce
