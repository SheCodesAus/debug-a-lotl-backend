import json
# URL-encode query params and API key for the Google Books request.
from urllib.parse import quote_plus
# Raised when Google Books API returns 4xx/5xx (e.g. 429 quota exceeded).
from urllib.error import HTTPError
# Fetch the Google Books API response; URLError for network/connection failures.
from urllib.request import urlopen, URLError

# GOOGLE_BOOKS_API_KEY is read from here for the BookSearch proxy.
from django.conf import settings
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Club
from .serializers import ClubSerializer


class ClubListCreate(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        if request.user.is_authenticated:
        # Show public clubs + clubs where user is owner/member
            clubs = Club.objects.filter(
                Q(is_public=True) |
                Q(owner=request.user) |
                Q(memberships__user=request.user, memberships__status="approved")
            ).distinct()
        else:
            # Anonymous users only see public clubs
            clubs = Club.objects.filter(is_public=True)

        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClubSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookSearch(APIView):
    """Proxy to Google Books API. Requires GOOGLE_BOOKS_API_KEY in env."""
    permission_classes = [AllowAny]

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        if not q:
            return Response([], status=status.HTTP_200_OK)

        api_key = getattr(settings, "GOOGLE_BOOKS_API_KEY", "") or ""
        if not api_key:
            return Response(
                {"error": "Google Books API key not configured (GOOGLE_BOOKS_API_KEY)."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        encoded_q = quote_plus(q)
        url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q={encoded_q}&maxResults=20&printType=books&key={quote_plus(api_key)}"
        )
        try:
            with urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
        except HTTPError as e:
            try:
                body = e.fp.read().decode() if e.fp else ""
            except Exception:
                body = ""
            try:
                err_data = json.loads(body)
                msg = err_data.get("error", {}).get("message", body or str(e))
            except json.JSONDecodeError:
                msg = body or str(e)
            return Response(
                {"error": "Google Books API error.", "detail": msg},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except (URLError, OSError, json.JSONDecodeError) as e:
            return Response(
                {"error": "Error calling Google Books API.", "detail": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        items = data.get("items") or []
        results = []
        for item in items:
            vi = item.get("volumeInfo") or {}
            links = vi.get("imageLinks") or {}
            results.append({
                "google_books_id": item.get("id"),
                "title": vi.get("title") or "Untitled",
                "author": ", ".join(vi.get("authors") or ["Unknown author"]),
                "description": vi.get("description") or "",
                "cover_image": links.get("thumbnail") or links.get("smallThumbnail") or "",
                "published_date": vi.get("publishedDate"),
            })
        return Response(results, status=status.HTTP_200_OK)
