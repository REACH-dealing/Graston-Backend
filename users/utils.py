from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
import random
import jwt
from Graston.settings import SECRET_KEY
from .models import User, VerificationRequests


def regenerate_otp(instance):
    """
    Utility function to regenerate OTP for the given user.
    """

    if instance.otp_max_try == 0 and datetime.datetime.now(datetime.UTC) < instance.otp_max_out:
        return [Response(
            "Max OTP try reached, try after a three minutes",
            status=status.HTTP_400_BAD_REQUEST,
        ), instance]

    instance.otp = random.randint(1000, 9999)
    instance.otp_expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=2
    )
    instance.otp_max_try = instance.otp_max_try - 1
    if instance.otp_max_try == 0:
        # Remember to edit max out to one hour
        instance.otp_max_out = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=3
        )

    elif instance.otp_max_try == -1:
        instance.otp_max_try = 3

    else:
        instance.otp_max_out = None
        # instance.otp_max_try = instance.otp_max_try

    instance.save()

    return [None, instance]


def send_otp2email_util(instance, html_file_name):
    """
    Utility function to send otp number to Email.
    """

    # Load the HTML content from a template file
    html_content = render_to_string(f"{html_file_name}", {"otp": instance.otp})
    plain_message = strip_tags(html_content)  # Fallback for plain-text email

    try:
        send_mail(
            subject="Activate your Graston account",
            message=plain_message,
            from_email=None,
            recipient_list=[instance.email],
            html_message=html_content,
            fail_silently=False,
        )
        

        return Response({
            "user_id": instance.user.id,
            "message": f"We sent otp number to your email: {instance.email}",     
        }, status=status.HTTP_200_OK,)
        

    except Exception as e:
        return Response(e, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def send_otp2phone_util(user_id):
	"""
	Utility function to send otp number to phone.
	"""
	pass

def get_tokens(user):
    """
    Utility function to generate access and refresh tokens
    """
    access_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=61),
        "iat": datetime.datetime.now(datetime.UTC),
        "refresh": False,
    }

    refresh_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=70),
        "iat": datetime.datetime.now(datetime.UTC),
        "refresh": True,
    }

    # remember to search about best encoding algorithm & add the algorithm name to .env file
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token
