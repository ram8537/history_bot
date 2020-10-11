from rest_framework import serializers
from .models import Items, FAQ


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ['item_number', 'title', 'image', 'description']


class ReactFilteredResponseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'confidence_score': instance['passage_score'],
            'text': instance['passage_text'],
        }


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['item_number', 'question', 'answer']
