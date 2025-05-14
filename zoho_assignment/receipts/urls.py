from django.urls import path
from .views import UploadReceiptView, ValidateReceiptView, ProcessReceiptView, ListReceiptsView, GetReceiptView

urlpatterns = [
    path('upload/', UploadReceiptView.as_view()),
    path('validate/', ValidateReceiptView.as_view()),
    path('process/', ProcessReceiptView.as_view()),
    path('receipts/', ListReceiptsView.as_view()),
    path('receipts/<int:pk>/', GetReceiptView.as_view()),
]
