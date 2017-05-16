import json

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from djcelery.models import PeriodicTask, CrontabSchedule

from apps.mentions.models import Merchant, Account
from apps.users.models import AppUser, APIKey


@receiver(post_save, sender=Merchant)
def add_periodic_task_for_merchant(sender, instance, created, **kwargs):
    """Post-save signal for Merchant's model.

    This function called on saving of merchant from core of Django and
    creates celery periodic tasks to search mentions and analyse it.

    Args:
      sender (object): class of saved model instance.
      instance (object): saved instance of Merchant model.
      created (bool): is instance created or updated.

    """
    if created:
        # create account for new merchant
        account = Account.objects.create(
            company_name=instance.official_name,
            type=Account.MERCHANT
        )
        account.merchants.add(instance)
        semant_key = APIKey.objects.filter(api_type=APIKey.SEMANTRIA).first()
        google_key = APIKey.objects.filter(api_type=APIKey.GOOGLE).first()

        if semant_key:
            semant_key.account.add(account)
        if google_key:
            google_key.account.add(account)

        cron_search = CrontabSchedule.objects.get_or_create(hour=6, minute=1)

        PeriodicTask.objects.create(
            name='search_{0}'.format(instance.id),
            task='apps.mentions.tasks.get_query',
            crontab=cron_search[0],
            enabled=True,
            kwargs=json.dumps({'merchant_id': instance.id})
        )
    else:
        # update company name for related models
        instance.account_set.filter(
            type=Account.MERCHANT
        ).update(
            company_name=instance.official_name
        )


@receiver(post_delete, sender=Merchant)
def remove_periodic_tasks(sender, instance, using, **kwargs):
    """Post-delete signal for the Merchant's model.

    Function to delete users, accounts and periodic task if respective
    merchant was deleted.

    Args:
      sender (object): class of saved model instance
      instance (object): deleted instance of Merchant model
      using (str): The database alias being used.

    """
    PeriodicTask.objects.filter(name='search_{0}'.format(instance.id)).delete()
    accounts = instance.account_set.filter(type=Account.MERCHANT)
    users = AppUser.objects.filter(account__in=accounts)
    accounts.delete()
    users.delete()
