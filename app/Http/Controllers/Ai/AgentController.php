<?php

namespace App\Http\Controllers\Ai;

use App\Http\Controllers\Controller;
use App\Services\Ai\AiAgent;
use Illuminate\Http\Client\RequestException;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Throwable;

class AgentController extends Controller
{
    public function index(){
        return view('ai.agent');
    }

    //agent post


    public function post(Request $request, AiAgent $aiAgent){
        $request->validate([
            'message' => 'required|string|max:2000',
        ]);
        $message = $request->message;

        try {
            $response = $aiAgent->run([
                [
                    'role' => 'user',
                    'content' => $message,
                ]
            ]);
        } catch (RequestException $e) {
            Log::error('Anthropic API hatası', ['status' => $e->response->status(), 'body' => $e->response->json()]);

            return response()->json(['message' => 'AI servisine ulaşılamadı. Lütfen tekrar dene.'], 502);
        } catch (Throwable $e) {
            Log::error('AI agent hatası', ['exception' => $e]);

            return response()->json(['message' => 'Beklenmeyen bir hata oluştu.'], 500);
        }

        return response()->json([
            'reply' => AiAgent::text($response) ?: 'Bir cevap üretilemedi.',
        ]);
    }
}
