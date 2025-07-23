from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from datetime import timezone as dt_timezone  

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        issued_at_timestamp = validated_token.get("iat")
        if issued_at_timestamp is None:
            raise AuthenticationFailed('Token has no issued-at (iat) claim')

        issued_at = timezone.datetime.fromtimestamp(issued_at_timestamp, tz=dt_timezone.utc)

        if user.token_valid_after and issued_at < user.token_valid_after:
            raise AuthenticationFailed('Token has been invalidated')

        return user
