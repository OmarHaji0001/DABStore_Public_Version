from django.db import models
from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.
class singilatonModel(models.Model):
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class Theme(singilatonModel):
    name = models.CharField(max_length=100)
    slogan = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='theme/%Y/%m/%d/%H/%M/%S')
    banner = models.ImageField(upload_to='theme/%Y/%m/%d/%H/%M/%S')
    about = models.TextField()
    instagram = models.URLField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    about2 = RichTextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    genderList = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Both', 'Both'),
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=genderList, default='Both')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    image = models.ImageField(upload_to='product/%Y/%m/%d/%H/%M/%S')
    quantity = models.IntegerField(default=1)
    number_of_sales = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number field must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    wahatsappPrefix = [('----','----'),('+972','+972'),('+970','+970')]
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = CustomUserManager()
    whatsapp = models.CharField(max_length=15, choices=wahatsappPrefix, default='----')
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.phone_number


class UserProductOrder(models.Model):
    statusList = [
        ('pending', 'pending'),
        ('ordered', 'ordered'),
        ('Delivered', 'Delivered'),

    ]
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    order_id = models.IntegerField(default=-1)
    status = models.CharField(max_length=10, choices=statusList, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.product.name} by {self.user.phone_number}"

    @property
    def total_price(self):
        return self.product.discount * self.quantity if self.product.discount > 0 else self.product.price * self.quantity

from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Orders(models.Model):
    statusList = [
        ('بانتظار التأكيد', 'بانتظار التأكيد'),
        ('تم التأكيد', 'تم التأكيد'),
        ('تم التسليم', 'تم التسليم'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=statusList, default='بانتظار التأكيد')
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    address = models.TextField()
    delivered_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.phone_number} - {self.status} - {self.user.first_name} {self.user.last_name}"

class MultiImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product/%Y/%m/%d/%H/%M/%S')
    def __str__(self):
        return self.product.name