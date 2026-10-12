<p align="right"><a href="README.md">Türkçe</a> · <b>English</b></p>

# Sipariş Asistanı (Order Assistant)

> A Turkish-speaking customer service assistant built with Laravel and Anthropic Claude.

[![Tests](https://github.com/bykeremx/anthropic-agent-laravel/actions/workflows/tests.yml/badge.svg)](https://github.com/bykeremx/anthropic-agent-laravel/actions/workflows/tests.yml)

Users ask questions in natural language in a chat window. When needed, the model queries the database through **tool use (function calling)** and answers based on real data.

![Chat screen: an order status query and a customer orders query](.github/images/chat-screenshot.png)

```
"ORD-1003 siparişinin durumu ne?"          (What is the status of order ORD-1003?)
        → the model calls the get_order_status tool
        → Laravel reads the order from the database
        → "ORD-1003 numaralı sipariş beklemede, tutarı 3.200,00 TL."
          (Order ORD-1003 is pending, total 3,200.00 TRY.)
```

## Features

- **Agent loop:** the model requests a tool → the app runs it → the result is fed back to the model; at most 5 rounds.
- **Two tools:**
  - `get_customer_orders` — searches customers by first/last name (up to 5 matches) and returns their orders plus total spent, excluding cancelled orders.
  - `get_order_status` — fetches a single order by its number (inputs like `1003` or `ord-1003` are normalized to `ORD-1003`).
- **Safe tool dispatch:** the model can only run tools declared in `ToolSchema`.
- **No extra SDK:** requests go straight to the Anthropic Messages API through Laravel's `Http` client.
- **Error handling:** API errors return 502 and unexpected errors return 500; both are logged, and no internal details reach the user.

## Architecture

```
Browser (x-ai.chat)
   │  POST /ai/agent/send  {message}
   ▼
AgentController ── validation (required|string|max:2000)
   │
   ▼
AiAgent::run() ─────────────► ToolSchema::all()   (tool definitions shown to the model)
   │   ▲
   │   │ tool_result
   ▼   │
AiClient::send() ──► Anthropic Messages API
   │
   │ stop_reason == tool_use ?
   ├── yes ──► ToolsService::call() ──► Eloquent (customers, orders)
   └── no ───► AiAgent::text() ──► {"reply": "..."}
```

| File | Responsibility |
|---|---|
| `app/Http/Controllers/Ai/AgentController.php` | HTTP entry point: validates, runs the agent, turns the reply or error into JSON |
| `app/Services/Ai/AiAgent.php` | Orchestrator: system prompt, tool list, bounded tool-use loop |
| `app/Services/Ai/AiClient.php` | A single HTTP call to the Anthropic Messages API |
| `app/Services/Ai/ToolsService.php` | Tool implementations (Eloquent queries, whitelist check) |
| `app/Schema/ToolSchema.php` | Tool definitions shown to the model (name, description, JSON Schema) |
| `resources/views/components/ai/chat.blade.php` | Chat UI |

## Requirements

- PHP **8.4+** (required by `composer.lock`)
- Composer
- Node.js and npm (for frontend assets)
- SQLite (default) or any database supported by Laravel
- An [Anthropic API key](https://console.anthropic.com/)

## Installation

```bash
git clone https://github.com/bykeremx/anthropic-agent-laravel.git
cd anthropic-agent-laravel

composer install
cp .env.example .env
php artisan key:generate
```

Add your Anthropic settings to `.env`:

```dotenv
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-5-5
```

Create the database and fill it with sample data (30 customers, 100 orders):

```bash
touch database/database.sqlite      # if you use SQLite
php artisan migrate --seed
```

Build the frontend assets:

```bash
npm install
npm run build
```

## Running

- **Laravel Herd:** the project is served automatically under its folder name (e.g. `http://anthropic-agent-laravel.test`).
- **Without Herd:** `composer run dev` (runs the server, queue and Vite together) or `php artisan serve`.

Assistant page: **`/ai/agent`**

The assistant answers in Turkish. Sample questions that work with the seed data:

- `Ahmet Yılmaz'ın siparişleri neler?` (What are Ahmet Yılmaz's orders?)
- `ORD-1003 siparişinin durumu ne?` (What is the status of order ORD-1003?)
- `Ayşe Demir toplam ne kadar harcamış?` (How much has Ayşe Demir spent in total?)
- `Mehmet isimli müşterilerin siparişlerini listele.` (List the orders of customers named Mehmet.)

## Endpoints

| Method | URL | Route name | Description |
|---|---|---|---|
| GET | `/ai/agent` | `ai.agent` | Chat page |
| POST | `/ai/agent/send` | `ai.send` | Sends a message (`{"message": "..."}`) |

Responses (messages are returned in Turkish):

| Status | Body |
|---|---|
| 200 | `{"reply": "..."}` |
| 422 | Validation error (`{"message": "...", "errors": {...}}`) |
| 502 | `{"message": "AI servisine ulaşılamadı. Lütfen tekrar dene."}` (Could not reach the AI service. Please try again.) |
| 500 | `{"message": "Beklenmeyen bir hata oluştu."}` (An unexpected error occurred.) |

> The POST route is in the `web` middleware group, so it requires an `X-CSRF-TOKEN` header.

## Tests

Tests are written with [Pest](https://pestphp.com). The Anthropic API is faked with `Http::fake()`, so **no API key is needed and no request leaves your machine.**

```bash
php artisan test
```

| Test file | Coverage |
|---|---|
| `tests/Feature/Http/Controllers/Ai/AgentControllerTest.php` | Page, validation, successful reply, 502/500 error paths |
| `tests/Feature/Services/Ai/AiAgentTest.php` | Agent loop, tool_result matching, parallel tools, 5-step limit |
| `tests/Feature/Services/Ai/AiClientTest.php` | Headers, payload, exception on error responses |
| `tests/Feature/Services/Ai/ToolsServiceTest.php` | Customer/order queries, normalization, whitelist |
| `tests/Unit/Schema/ToolSchemaTest.php` | Every tool definition maps to a `ToolsService` method |

### Continuous integration

`.github/workflows/tests.yml` runs the tests on PHP 8.4 on every push to `main`/`master` and on every pull request. You can also start it manually from **Actions → Tests → Run workflow** on GitHub. No secrets are required.

## Adding a new tool

1. Add the definition to the `all()` array in `app/Schema/ToolSchema.php`: a `name`, a `description` that says when to use the tool (and when not to), and an `input_schema`.
2. Add a public method **with the same name** to `app/Services/Ai/ToolsService.php`. It must accept `array $input` and return either `['status' => 'success', ...]` or `['status' => 'error', 'message' => '...']`.
3. If needed, add a behavior rule for the tool to the system prompt in `AiAgent`.
4. Write its tests in `ToolsServiceTest.php`. `ToolSchemaTest` automatically checks that the definition and the method match.

## Known limitations

- Conversation history is not kept; each message is handled on its own.
- The AI endpoints have no authentication or rate limiting. Add the `auth` and `throttle` middleware before going to production.
- Customer names, emails, cities and order details are sent to the Anthropic API; review this against applicable data protection rules (KVKK, GDPR).

## License

[MIT](https://opensource.org/licenses/MIT)
