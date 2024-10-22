from .validators import *
from django.db import models
from wsgiref.validate import validator

#added




class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_account_active = models.BooleanField(default=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    

class Artist(models.Model):
    artist_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artists', null=True, blank=True)
    first_name = models.CharField(max_length=255, validators=[ValidateNameImpl])
    last_name = models.CharField(max_length=255, validators=[ValidateNameImpl])
    username = models.CharField(max_length=255, unique=True, validators=[ValidateUserNameImpl])
    password = models.CharField(max_length=255)  # Should be hashed in practice
    email = models.EmailField(max_length=255, unique=True, validators=[ValidateEmailImpl])
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20, validators=[ValidatePhoneNumberImpl])
    is_account_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Artwork(models.Model):
    artwork_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artworks')
    title = models.CharField(max_length=255, validators=[ValidateTitleImpl])
    description = models.TextField(validators=[ValidateTitleImpl])
    artwork_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[ValidatePriceImpl])
    image_path = models.ImageField(max_length=255, blank=True, null=True)
    video_path = models.FileField(max_length=255, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='requests')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='requests')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('fulfilled', 'Fulfilled'), ('canceled', 'Canceled')])
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True)
    #is_video = models.BooleanField(default=False)
    video_path = models.CharField(max_length=255, blank=True, null=True)
    #is_image = models.BooleanField(default=False)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    artist_accept_date = models.DateTimeField(blank=True, null=True)
    artist_delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Request {self.request_id} by {self.user}"


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.feedback_id} from {self.user}"


class ArtistProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='profiles')
    bio = models.TextField()
    website = models.URLField(blank=True, null=True)
    social_links = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.artist}"


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='orders')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')])
    created_at = models.DateTimeField(auto_now_add=True)
    artist_delivery_date = models.DateTimeField(null=True   )
    actual_delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.username} - Artwork: {self.artwork.title} - Status: {self.order_status.capitalize()} - Total: ${self.total_price:.2f}"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer')])
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')])
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order}"


class Upload(models.Model):
    upload_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='uploads')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='uploads')
    file_path = models.CharField(max_length=255)
    upload_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Upload {self.upload_id} by {self.artist}"
