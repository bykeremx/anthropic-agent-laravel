<x-ai-layout>
    <x-slot:title>AI Asistan</x-slot:title>

    <x-ai.chat
        :endpoint="route('ai.send')"
        title="AI Asistan"
        subtitle="Müşteri ve siparişler hakkında soru sor."
        placeholder="Bir soru sor…"
        :suggestions="[
            'Ahmet Yılmaz’ın siparişleri neler?',
            'ORD-1003 siparişinin durumu ne?',
            'Ayşe Demir toplam ne kadar harcamış?',
            'Mehmet isimli müşterilerin siparişlerini listele.',
        ]"
    />
</x-ai-layout>
