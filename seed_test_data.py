import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from users.models import CustomUser
from analytics.models import Campaign, AdCreative

# --- 1. ОЧИЩЕННЯ ДАНИХ ---
print("Очищення старої бази даних...")
Campaign.objects.all().delete()  # AdCreative видаляться автоматично через CASCADE

# --- 2. НАЛАШТУВАННЯ ГЕНЕРАЦІЇ ---
buyers = CustomUser.objects.filter(role='media_buyer')
if not buyers.exists():
    print("Помилка: Баєрів не знайдено! Спершу створи користувачів з роллю 'media_buyer'.")
else:
    campaign_names = ["TikTok_Scale", "CPA_Nutra_US", "Gadget_Promo", "Fashion_Summer", "App_Install_Global",
                      "InFeed_Test_V2"]
    statuses = ['ACTIVE', 'PAUSED', 'COMPLETED']
    today = timezone.now().date()

    for buyer in buyers:
        print(f"Генерація 15 кампаній для: {buyer.username}...")

        for i in range(15):
            # Робота з датами
            start_date = today - timedelta(days=random.randint(10, 60))
            p_date = None
            e_date = None

            status = random.choice(statuses)
            if status == 'PAUSED':
                p_date = start_date + timedelta(days=random.randint(5, 9))
            elif status == 'COMPLETED':
                e_date = start_date + timedelta(days=random.randint(10, 20))

            # Фінансові показники
            budget = Decimal(random.randrange(1000, 10000))
            spend = Decimal(random.uniform(200, float(budget))).quantize(Decimal('0.00'))

            # Маркетингові показники
            impressions = random.randint(50000, 500000)
            clicks = random.randint(1000, int(impressions * 0.08))
            conversions = random.randint(20, int(clicks * 0.15))

            # Створення кампанії
            campaign = Campaign.objects.create(
                owner=buyer,
                name=f"{random.choice(campaign_names)}_{i + 1}",
                status=status,
                budget=budget,
                spend=spend,
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                start_date=start_date,
                pause_date=p_date,
                end_date=e_date
            )

            # Створення 1-3 креативів для кожної кампанії
            for c in range(random.randint(1, 3)):
                # Кожен 3-й креатив робимо з поганим ROI для тесту вигорання
                if random.random() < 0.3:
                    roi = Decimal(random.uniform(-50, 15)).quantize(Decimal('0.00'))
                    burning = True
                else:
                    roi = Decimal(random.uniform(40, 300)).quantize(Decimal('0.00'))
                    burning = False

                AdCreative.objects.create(
                    campaign=campaign,
                    title=f"Creative_V{random.randint(1, 9)}_{random.randint(100, 999)}",
                    duration=random.choice([10, 15, 20, 30]),
                    hook=random.choice(["Stop scrolling!", "Wait for the end", "Limited offer", "Check this out"]),
                    spend=spend / Decimal(random.randint(1, 3)),
                    roi=roi,
                    is_burning_out=burning
                )

    print("--- УСПІШНО: Базу очищено та заповнено новими даними (15 на баєра) ---")