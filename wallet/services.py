from django.utils import timezone
from decimal import Decimal
from .models import *
from core.models import CustomUser


def process_confirmed_transaction(transaction):
    if transaction.action == Transaction.ACTION_DEPOSIT:
        asset = transaction.asset
        confirmed_at = timezone.now()

        time_difference = confirmed_at - asset.confirmed_at

        calculated_profit = Decimal(asset.amount) * Decimal(asset.level.profit_rate) * Decimal(time_difference.days)

        user = asset.user
        user.credit += calculated_profit
        user.save()

        asset.amount += transaction.amount
        asset.confirmed_at = confirmed_at
        asset.save()

        # Create a profit transaction
        profit_transaction = Transaction.objects.create(
            action=Transaction.ACTION_PROFIT,
            amount=calculated_profit,
            status=Transaction.STATUS_CONFIRMED,
            created_at= timezone.now(),
            updated_at= timezone.now(),
            asset=asset,
            user=user
        )

    elif transaction.action == Transaction.ACTION_WITHDRAW:
        asset = transaction.asset
        confirmed_at = asset.confirmed_at
        now = timezone.now()
        time_difference = now - confirmed_at

        if time_difference.days < 30:
            asset.amount -= transaction.amount
        else:

            calculated_profit = Decimal(asset.amount) * Decimal(asset.level.profit_rate) * Decimal(time_difference.days)

            user = asset.user
            user.credit += calculated_profit
            user.save()

            asset.amount -= transaction.amount

            # Create a profit transaction
            profit_transaction = Transaction.objects.create(
                action=Transaction.ACTION_PROFIT,
                amount=calculated_profit,
                status=Transaction.STATUS_CONFIRMED,
                created_at= timezone.now(),
                updated_at= timezone.now(),
                asset=asset,
                user=user
            )

        asset.confirmed_at = now
        asset.save()

def update_asset_level(asset):
    user = asset.user
    referred_users_count = CustomUser.objects.filter(referrer=user.referral_token).count()

    eligible_levels = Level.objects.filter(min_referral__lte=referred_users_count, min_deposit__lte=asset.amount).order_by('-min_deposit', '-min_referral')

    if eligible_levels.exists():
        best_level = eligible_levels.first()
        asset.level = best_level
        asset.save()
