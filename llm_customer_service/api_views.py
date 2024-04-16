import json
from .models import Conversation
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .views import call_gemini_api

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_gemini_api(request):
    if request.method == 'POST':
        try:
            user_id = request.user.id
            
            user_input = json.loads(request.body).get('message')
            
            
            previous_conversations = Conversation.objects.filter(user_id=user_id).order_by('-timestamp')[:20]
            dialog_history = "\n".join([conv.message + "\n" + conv.response for conv in reversed(previous_conversations)])

            
            response = call_gemini_api(user_input, dialog_history)

            
            new_conversation = Conversation(user_id=user_id, message=user_input, response=response)
            new_conversation.save()

            return Response({'response': response})

        except Exception as e:
            return Response({'error': str(e)})

    return Response({'message': 'This is a POST endpoint.'})