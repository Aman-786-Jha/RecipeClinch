### for the schedule purpose celery beat

import csv
import boto3
from io import StringIO
from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@shared_task
def export_users_to_s3():
    try:
        User = get_user_model()
        users = User.objects.select_related('city').all()

        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        writer.writerow([
            'ID', 'Full Name', 'Email', 'Mobile Number', 'Country Code',
            'Gender', 'Age', 'City', 'Date of Birth', 'Date Joined',
            'User Type', 'Is Active', 'Is Mobile Verified', 'Is Superuser',
            'Is Staff', 'Is Rejected', 'Is Approved', 'Is Blocked',
            'Email Verified', 'Login Status', 'Email OTP Verified', 'Forgot OTP Verified',
            'Account OTP', 'Forgot OTP',
            'Account OTP Created At', 'Forgot OTP Created At',
            'Account OTP Resend Count', 'Forgot OTP Resend Count',
            'Account OTP Last Resend Time', 'Forgot OTP Last Resend Time',
            'Token Valid After'
        ])

        for user in users:
            writer.writerow([
                user.id,
                user.full_name or '',
                user.email,
                str(user.mobile_number),
                user.countrycode or '',
                user.gender or '',
                user.age or '',
                user.city.name if user.city else '',
                user.dob.strftime("%Y-%m-%d") if user.dob else '',
                user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if hasattr(user, 'date_joined') else '',
                user.user_type,
                user.is_active,
                user.is_mobile_verified,
                user.is_superuser,

                # Extended fields
                user.is_staff,
                user.is_rejected,
                user.is_aproved,
                user.is_blocked,
                user.email_verify,
                user.login_status,
                user.email_account_otp_verify,
                user.forget_otp_verify,
                user.account_otp or '',
                user.forgot_otp or '',
                user.account_otp_created_at.strftime('%Y-%m-%d %H:%M:%S') if user.account_otp_created_at else '',
                user.forgot_otp_created_at.strftime('%Y-%m-%d %H:%M:%S') if user.forgot_otp_created_at else '',
                user.account_otp_resend_count,
                user.forgot_otp_resend_count,
                user.account_last_otp_resend_time.strftime('%Y-%m-%d %H:%M:%S') if user.account_last_otp_resend_time else '',
                user.forgot_last_otp_resend_time.strftime('%Y-%m-%d %H:%M:%S') if user.forgot_last_otp_resend_time else '',
                user.token_valid_after.strftime('%Y-%m-%d %H:%M:%S') if user.token_valid_after else '',
            ])

        file_name = f"weekly_exports/users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )

        logger.info(f"Exported user data to S3 as {file_name}")

    except Exception as e:
        logger.error(f"Failed to export user data to S3: {e}")
