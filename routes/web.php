<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});


Route::get('/ai/agent', [App\Http\Controllers\Ai\AgentController::class, 'index'])->name('ai.agent');

//ai sende messages

Route::post('/ai/agent/send', [App\Http\Controllers\Ai\AgentController::class, 'post'])->name('ai.send');
