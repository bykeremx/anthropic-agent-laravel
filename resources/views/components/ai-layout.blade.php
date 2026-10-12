<!DOCTYPE html>
<html style="color-scheme: light" lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="h-full">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ $title ?? 'AI Asistan' }} · {{ config('app.name', 'Laravel') }}</title>

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="h-full bg-zinc-50 text-zinc-900 antialiased">
        {{ $slot }}

        @stack('scripts')
    </body>
</html>

