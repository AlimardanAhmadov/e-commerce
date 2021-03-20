from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from django.template.defaultfilters import slugify
from main.models import Product
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    first_name = models.CharField(max_length=400, blank=True, null=True)
    last_name = models.CharField(max_length=400, blank=True, null=True)
    phone_number = models.CharField(max_length=400, blank=True, null=True)
    email = models.EmailField(max_length=400, blank=True, null=True)

    def __str__(self):
        return str(self.user.username)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='seller')
    first_name = models.CharField(max_length=400, blank=True, null=True)
    last_name = models.CharField(max_length=400, blank=True, null=True)
    phone_number = models.CharField(max_length=400, blank=True, null=True)
    email = models.EmailField(max_length=400, blank=True, null=True)
    company_name = models.CharField(max_length=400, blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Address(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True)
    region = models.CharField(max_length=250, blank=True)
    flat = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=150, blank=True)
    postcode = models.IntegerField(blank=True)
    default = models.BooleanField(default=False)
    address_type = models.CharField(max_length=20, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.address)
        super(Address, self).save(*args, **kwargs)

    def __str__(self):
        return self.owner.username


class WishListItem(models.Model):
    products = models.ManyToManyField(Product, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.profile.first_name
        

class SellerRequest(models.Model):
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    email = models.EmailField(max_length=500)
    phone = models.CharField(max_length=200)
    company_name = models.CharField(max_length=500)
    info = models.TextField()
    # approved = models.BooleanField(default=False)

    def __str__(self):
        return self.email + " (" + ("not " if not self.approved else "") + "approved)"    


class ApproveSellerEmail(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=150)
    contents = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.subject + " " + self.created_at.strftime("%B %d, %Y")

    def send(self, request):
        #contents = self.contents.read().decode('utf-8')
        requests = SellerRequest.objects.filter(approved=True)
        # send approvement email 
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        for request in requests:
            message = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=request.email,
                    subject=self.subject,
                    html_content=self.contents + (
                        '<br><p>Click here to create a seller account</p>.'))
            sg.send(message)
        requests.delete()
    