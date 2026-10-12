# Laravel AI Agent Test Veritabanı Yapısı

AI agent'ınızın tool'larını (örneğin: `get_customer_orders`, `get_customer_details`) test edebilmesi için gerekli olan `customers` ve `orders` tablolarının migration taslakları ve örnek verileri aşağıdadır.

## 1. Migration Taslakları

### `database/migrations/xxxx_xx_xx_create_customers_table.php`
```php
Schema::create('customers', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email')->unique();
    $table->string('phone')->nullable();
    $table->string('city');
    $table->timestamps();
});
```

### `database/migrations/xxxx_xx_xx_create_orders_table.php`
```php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('customer_id')->constrained()->onDelete('cascade');
    $table->string('order_number')->unique();
    $table->decimal('total_amount', 10, 2);
    $table->enum('status', ['pending', 'processing', 'completed', 'cancelled'])->default('pending');
    $table->text('notes')->nullable();
    $table->timestamps();
});
```

---

## 2. Model İlişkileri

Agent'ınızın Eloquent kullanarak veriyi kolayca çekebilmesi için ilişkileri şu şekilde tanımlayabilirsiniz:

**Customer Model (`app/Models/Customer.php`):**
```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Customer extends Model
{
    protected $fillable = ['name', 'email', 'phone', 'city'];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }
}
```

**Order Model (`app/Models/Order.php`):**
```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Order extends Model
{
    protected $fillable = ['customer_id', 'order_number', 'total_amount', 'status', 'notes'];

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }
}
```

---

## 3. Örnek Veriler (Seeder / Test Data)

Agent'a "Ahmet'in siparişleri nelerdir?" veya "ORD-1001 nolu siparişin durumu ne?" gibi sorular sorup tool'ları test etmek için bu verileri kullanabilirsiniz.

### Müşteriler (`customers` tablosu)
| id | name | email | phone | city |
|---|---|---|---|---|
| 1 | Ahmet Yılmaz | ahmet@example.com | 5551112233 | İstanbul |
| 2 | Ayşe Demir | ayse@example.com | 5554445566 | Ankara |
| 3 | Mehmet Kaya | mehmet@example.com | 5557778899 | İzmir |

### Siparişler (`orders` tablosu)
| id | customer_id | order_number | total_amount | status | notes |
|---|---|---|---|---|---|
| 1 | 1 | ORD-1001 | 1250.00 | completed | Kapıda ödeme seçildi. |
| 2 | 1 | ORD-1002 | 450.50 | processing | Hızlı kargo talep edildi. |
| 3 | 2 | ORD-1003 | 3200.00 | pending | Havale bekleniyor. |
| 4 | 3 | ORD-1004 | 890.00 | completed | Hediye paketi yapıldı. |
