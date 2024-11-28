from rest_framework import serializers
from myapp.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def validate(self, data):
        # Check if passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Create the user and set the password
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password1'])  # Hash the password before saving
        user.save()
        return user
    
class LoginForm(serializers.Serializer):
    identifier = serializers.CharField(label="Username or Email", max_length=150)
    password = serializers.CharField(write_only=True, max_length=128)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        # Attempt to find the user by username or email
        try:
            if '@' in identifier:
                user = CustomUser.objects.get(email=identifier)
            else:
                user = CustomUser.objects.get(username=identifier)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid username or email.")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password.")

        # Add user to validated_data
        data['user'] = user
        return data
    
