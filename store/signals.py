from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Product,Book

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

def save_user_profile(sender, instance, created, **kwargs):
    if created: 
        if not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Book)
def create_product_for_book(sender, instance, created, **kwargs):
    if created and not instance.product:  # Only create a product if one doesn't exist already
        product = Product.objects.create(
            name=f"Product for {instance.title}",
            price=instance.price,
            description=f"Default product for {instance.title}",
            book=instance
        )
        # Optionally, you can link the product back to the book
        instance.product = product
        instance.save()