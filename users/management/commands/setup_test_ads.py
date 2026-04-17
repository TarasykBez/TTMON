from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import TikTokAdAccount, TikTokIntegration

User = get_user_model()


class Command(BaseCommand):
    help = 'Призначає рекламний акаунт баєру для тестування'

    def handle(self, *args, **options):
        user = User.objects.get(username='buyer_t')  # твій юзернейм
        main_int = TikTokIntegration.objects.first()

        acc, created = TikTokAdAccount.objects.get_or_create(
            advertiser_id='7614550740572422145',
            defaults={
                'advertiser_name': 'TTMON_adv',
                'buyer': user,
                'main_integration': main_int,
                'status': 'ENABLE'
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Акаунт {acc.advertiser_name} успішно закріплено за {user.username}'))