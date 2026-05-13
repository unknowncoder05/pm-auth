from django.test import TestCase
from django.contrib.auth import get_user_model
from pm_auth.api.users.models.auth import ExternalAuthenticationToken
from pm_auth.api.users.enums import ExternalAuthenticationTokenType
from unittest.mock import patch

User = get_user_model()

class AuthModelsTestCase(TestCase):
    def setUp(self):
        # Patch send_token globally for this test class to avoid AWS errors
        self.send_token_patcher = patch('pm_auth.api.users.models.auth.send_token')
        self.mock_send_token = self.send_token_patcher.start()

        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            phone_number='+1234567890'
        )

    def tearDown(self):
        self.send_token_patcher.stop()

    def test_external_authentication_token_creation(self):
        token = ExternalAuthenticationToken.objects.create(
            user=self.user,
            type=ExternalAuthenticationTokenType.SIGN_IN
        )
        self.assertIsNotNone(token.token)
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.type, ExternalAuthenticationTokenType.SIGN_IN)

    def test_token_sign_up_signal(self):
        # Create an inactive user
        user = User.objects.create_user(
            email='inactive@example.com',
            password='password123',
            is_active=False,
            phone_number='+0987654321'
        )
        # Check if VALIDATE_ACCOUNT token was created via signal
        token = ExternalAuthenticationToken.objects.filter(
            user=user,
            type=ExternalAuthenticationTokenType.VALIDATE_ACCOUNT
        ).first()
        self.assertIsNotNone(token)
