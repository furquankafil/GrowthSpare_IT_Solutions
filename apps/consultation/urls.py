"""
URL configurations mapping consultation booking forms and scoping funnel paths
to custom views.
"""

from django.urls import path
from . import views

app_name = "consultation"

urlpatterns = [
    # Interactive Scoping Consultation Booking Page
    path("book/", views.ConsultationBookingView.as_view(), name="book"),
]