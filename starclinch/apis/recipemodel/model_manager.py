from django.contrib.auth.models import BaseUserManager

class StarclinchUserManager(BaseUserManager):

    def create_user(self, email, password):
        if not email:
            raise ValueError('Users must have an Email Address')

        user = self.model(
            email=self.normalize_email(email),
            is_active=False,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.model(email=email)
        user.set_password(password)
        user.is_superuser = True
        if user.is_superuser:
            user.full_name = "Developer"
            user.user_type = "Dev"
            user.is_staff = True
        
        user.is_active = True
        user.save(using=self._db)
        return user