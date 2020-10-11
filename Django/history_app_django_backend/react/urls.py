from django.urls import include, path
from .views import ItemsListView, ItemsDetailView, ReactWatsonAssistant, AssistantDiscovery, FAQListView

urlpatterns = [
    path('assistant-discovery', AssistantDiscovery.as_view()),
    path('watson', ReactWatsonAssistant.as_view()),
    path('faq/<int:item_number>', FAQListView.as_view()),
    path('<pk>', ItemsDetailView.as_view()),
    path('', ItemsListView.as_view()),
]
