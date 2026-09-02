from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import normalize_phone

User = get_user_model()   # resolves to accounts.User (AUTH_USER_MODEL)


class RegisterSerializer(serializers.ModelSerializer):
    # write_only → the password is accepted on input but never sent back in responses.
    # validate_password runs Django's AUTH_PASSWORD_VALIDATORS (min length, too-common,
    # all-numeric) — rejects weak passwords with a clear 400.
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'email', 'first_name', 'last_name']
        # KYC-style onboarding: names are required at sign-up (AbstractUser allows
        # blank by default, so we tighten it here at the API boundary).
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
        }

    def validate_phone_number(self, value):
        # Arabic digits to ASCII, so what we store is canonical 0-9.
        return normalize_phone(value)

    def create(self, validated_data):
        
        return User.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )


class ProfileSerializer(serializers.ModelSerializer):
    """The logged-in user's own profile (GET/PATCH /api/auth/me/)."""
    class Meta:
        model = User
        fields = ['phone_number', 'first_name', 'last_name', 'email']
        read_only_fields = ['phone_number']   # identity never changes via profile


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login serializer: normalize the phone number before authenticating, so a
    user who types Arabic digits still matches their ASCII-stored account."""
    def validate(self, attrs):
        attrs[self.username_field] = normalize_phone(attrs.get(self.username_field))
        return super().validate(attrs)
