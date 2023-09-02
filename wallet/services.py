from django.utils import timezone
from decimal import Decimal
from .models import *
from core.models import CustomUser


def process_confirmed_transaction(transaction):
    if transaction.action == Transaction.ACTION_DEPOSIT:
        asset = transaction.asset

        if asset.confirmed_at is None:
            asset.confirmed_at = timezone.now()
            asset.save()

        now = timezone.now()

        time_difference = now - asset.confirmed_at

        if asset.level:
            calculated_profit = Decimal(asset.amount) * Decimal(asset.level.profit_rate) * Decimal(time_difference.days)
            calculated_referral_profit = Decimal(asset.amount) * Decimal(asset.level.referral_profit_rate) * Decimal(time_difference.days)

            user = asset.user
            user.credit += calculated_profit
            user.save()

            if user.referrer:
                referrer = user.referrer
                referrer.credit += calculated_referral_profit
                referrer.save()

                # Create a transaction for the referrer's referral profit
                if calculated_referral_profit > 0:
                    referral_transaction = Transaction.objects.create(
                        action=Transaction.ACTION_PROFIT,
                        amount=calculated_referral_profit,
                        status=Transaction.STATUS_CONFIRMED,
                        created_at=timezone.now(),
                        updated_at=timezone.now(),
                        asset=referrer.asset,
                        user=user
                    )

            asset.amount += transaction.amount
            asset.confirmed_at = timezone.now()
            asset.save()

            if calculated_profit > 0:
                profit_transaction = Transaction.objects.create(
                    action=Transaction.ACTION_PROFIT,
                    amount=calculated_profit,
                    status=Transaction.STATUS_CONFIRMED,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                    asset=asset,
                    user=user
                )
        else:
            asset.amount += transaction.amount
            asset.confirmed_at = timezone.now()
            asset.save()

    elif transaction.action == Transaction.ACTION_WITHDRAW:
        asset = transaction.asset
        
        if asset.confirmed_at is None:
            asset.confirmed_at = timezone.now()
            asset.save()

        now = timezone.now()
        time_difference = now - asset.confirmed_at

        user = asset.user

        if time_difference.days < 30:
            if user.credit >= transaction.amount:
                user.credit -= transaction.amount
            else:
                remaining_amount = transaction.amount - user.credit
                user.credit = 0
                asset.amount -= remaining_amount

        else:
            if asset.level:
                calculated_profit = Decimal(asset.amount) * Decimal(asset.level.profit_rate) * Decimal(time_difference.days)
                print(asset.level)
                # calculated_referral_profit = Decimal(asset.amount) * Decimal(asset.level.referral_profit_rate) * Decimal(time_difference.days)

                user = asset.user
                user.credit += calculated_profit

                # if user.referrer:
                #     referrer = user.referrer
                #     referrer.credit += calculated_referral_profit
                #     referrer.save()

                if user.credit >= transaction.amount:
                    user.credit -= transaction.amount

                else:
                    remaining_amount = transaction.amount - user.credit
                    user.credit = 0
                    asset.amount -= remaining_amount
                # Check if asset amount is non-negative before saving
                if asset.amount >= 0:
                    user.save()
                    asset.confirmed_at = now
                    asset.save()

                    # Create a transaction for the referrer's referral profit
                    if calculated_referral_profit > 0:
                        referral_transaction = Transaction.objects.create(
                            action=Transaction.ACTION_PROFIT,
                            amount=calculated_referral_profit,
                            status=Transaction.STATUS_CONFIRMED,
                            created_at=timezone.now(),
                            updated_at=timezone.now(),
                            asset=referrer.asset,
                            user=user
                            )
                        
                    if calculated_profit > 0:
                        profit_transaction = Transaction.objects.create(
                            action=Transaction.ACTION_PROFIT,
                            amount=calculated_profit,
                            status=Transaction.STATUS_CONFIRMED,
                            created_at= timezone.now(),
                            updated_at= timezone.now(),
                            asset=asset,
                            user=user
                        )
                    
                else:
                    # Reject the transaction and set the status
                    transaction.status = Transaction.STATUS_REJECTED
                    transaction.save()
            else:
                if user.credit >= transaction.amount:
                    user.credit -= transaction.amount

                else:
                    remaining_amount = transaction.amount - user.credit
                    user.credit = 0
                    asset.amount -= remaining_amount 
                    
                if asset.amount >= 0:
                    user.save()
                    asset.confirmed_at = now
                    asset.save() 

def update_asset_level(asset):
    user = asset.user
    referred_users = CustomUser.objects.filter(referrer=user)
    filtered_referred_users = referred_users.filter(
            asset__confirmed_at__isnull=False,
            asset__level__isnull=False
        )
    referred_users_count = filtered_referred_users.count()
    eligible_levels = Level.objects.filter(
        min_referral__lte=referred_users_count,
        min_deposit__lte=asset.amount
    ).order_by('-min_deposit', '-min_referral')

    if eligible_levels.exists():
        best_level = eligible_levels.first()
        asset.level = best_level
        asset.save()
    
    else:
        # If no eligible levels found, set user's level to "none"
        asset.level = None
        asset.save()

        # Check if the user has a referrer and recursively update its level
    if user.referrer:
        referrer_asset = user.referrer.asset
        update_asset_level(referrer_asset)
