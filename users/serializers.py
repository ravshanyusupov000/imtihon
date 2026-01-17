from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email_or_phone", "password"]

    def validate(self, attrs):
        v = attrs["email_or_phone"].strip()
        if "@" in v:
            attrs["email"] = v.lower()
        else:
            attrs["phone"] = v
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("email_or_phone", None)

        if not validated_data.get("username"):
            base = (validated_data.get("email") or validated_data.get("phone") or "user").replace("@", "_")
            validated_data["username"] = base[:30]

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "first_name", "last_name"]
