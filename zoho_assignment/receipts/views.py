import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from rest_framework import status, views
from rest_framework.response import Response
from django.utils import timezone
from .models import ReceiptFile, Receipt
from .serializers import ReceiptFileSerializer, ReceiptSerializer


class UploadReceiptView(views.APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        receipt_file = ReceiptFile.objects.create(
            file_name=file.name,
            file_path=file,
        )
        return Response(ReceiptFileSerializer(receipt_file).data)


class ValidateReceiptView(views.APIView):
    def post(self, request):
        receipt_id = request.data.get('id')
        try:
            receipt_file = ReceiptFile.objects.get(id=receipt_id)
            if receipt_file.file_path.name.endswith('.pdf'):
                receipt_file.is_valid = True
                receipt_file.invalid_reason = ""
            else:
                receipt_file.is_valid = False
                receipt_file.invalid_reason = "Not a PDF file"
            receipt_file.save()
            return Response(ReceiptFileSerializer(receipt_file).data)
        except ReceiptFile.DoesNotExist:
            return Response({"error": "File not found"}, status=404)


class ProcessReceiptView(views.APIView):
    def post(self, request):
        breakpoint()
        receipt_id = request.data.get('id')
        try:
            receipt_file = ReceiptFile.objects.get(id=receipt_id)
            if not receipt_file.is_valid:
                return Response({"error": "File is not valid PDF"}, status=400)

            file_path = receipt_file.file_path.path
            images = convert_from_path(file_path)

            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)

            # Very basic info extraction (can be improved with NLP/AI)
            merchant = "Unknown"
            total = None
            date = None
            for line in text.splitlines():
                if "total" in line.lower():
                    try:
                        total = float(''.join(c for c in line if c.isdigit() or c == '.'))
                    except:
                        pass
                if "date" in line.lower() or "purchased" in line.lower():
                    date = timezone.now()  # Placeholder

            receipt = Receipt.objects.create(
                purchased_at=date,
                merchant_name=merchant,
                total_amount=total,
                file_path=receipt_file
            )

            receipt_file.is_processed = True
            receipt_file.save()

            return Response(ReceiptSerializer(receipt).data)
        except ReceiptFile.DoesNotExist:
            return Response({"error": "File not found"}, status=404)


class ListReceiptsView(views.APIView):
    def get(self, request):
        receipts = Receipt.objects.all()
        return Response(ReceiptSerializer(receipts, many=True).data)


class GetReceiptView(views.APIView):
    def get(self, request, pk):
        try:
            receipt = Receipt.objects.get(id=pk)
            return Response(ReceiptSerializer(receipt).data)
        except Receipt.DoesNotExist:
            return Response({"error": "Receipt not found"}, status=404)
