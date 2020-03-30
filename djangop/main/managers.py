from django.contrib.auth.base_user import BaseUserManager

#Currently the only required fields for the user are email and password, this should be updated in the future
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self,email,password, **extra_fields):

        #Make sure all required fields are these
        if not email:
            raise ValueError("The given email must be set")
        if not password:
            raise ValueError("A password is required")


        #Set all data and save the user
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password,  **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

