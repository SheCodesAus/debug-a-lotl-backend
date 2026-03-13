import json
# URL-encode query params and API key for the Google Books request.
from urllib.parse import quote_plus
# Raised when Google Books API returns 4xx/5xx (e.g. 429 quota exceeded).
from urllib.error import HTTPError
# Fetch the Google Books API response; URLError for network/connection failures.
from urllib.request import urlopen, URLError

# GOOGLE_BOOKS_API_KEY is read from here for the BookSearch proxy.
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Meeting, AnnouncementThread, Club, Member
from .serializers import (ClubSerializer, MeetingSerializer,AnnouncementThreadSerializer, MemberSerializer)
from .permissions import IsOwnerOrReadOnly



class ClubListCreate(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        if request.user.is_authenticated:
         # Authenticated users can see:
            # - public clubs
            # - clubs they own
            # - clubs where they are approved members
            clubs = Club.objects.filter(
                Q(is_public=True) |
                Q(owner=request.user) |
                Q(memberships__user=request.user, memberships__status = Member.STATUS_APPROVED)
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
    
class MeetingListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        meetings = Meeting.objects.filter(club_id=club_id)
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data)

    def post(self, request, club_id):
        club = Club.objects.get(pk=club_id)
        # Check if user is owner before allowing meeting creation
        if club.owner != request.user:
            return Response({"detail": "Only the owner can create meetings."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(club=club) # Automatically link to the club
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AnnouncementListCreate(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, club_id):
        announcements = AnnouncementThread.objects.filter(club_id=club_id)
        serializer = AnnouncementThreadSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request, club_id):
        club = Club.objects.get(pk=club_id)
        # Check if the person posting is the owner
        if club.owner != request.user:
            return Response({"detail": "Only the owner can post announcements."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AnnouncementThreadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(club=club)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ClubDetail(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        club = get_object_or_404(Club, pk=pk)
        # Private clubs should only be visible to owner or approved members.
        if not club.is_public:
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required for private clubs."},
                    status = status.HTTP_401_UNAUTHORIZED,
                )
            is_approved_member = Member.objects.filter(
                club=club,
                user=request.user,
                status=Member.STATUS_APPROVED,
            ).exists()

            if request.user != club.owner and not is_approved_member:
                return Response(
                    {"detail": "You do not have permissions to view this club"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        serializer = ClubSerializer(club)
        return Response(serializer.data)

class ClubJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        club = get_object_or_404(Club, pk=pk)

        if request.user == club.owner:
            return Response (
                {"detail": "Club owner does not need to join as a member."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        existing_member = Member.objects.filter(user=request.user, club=club).first()
        if existing_member:
            serializer = MemberSerializer(existing_member)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        membership_status = ( Member.STATUS_APPROVED if club.is_public else Member.STATUS_PENDING)
        member = Member.objects.create(
            user=request.user,
            club=club,
            status=membership_status,
        )

        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ClubMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        club = get_object_or_404(Club, pk=pk)
            
        if request.user != club.owner:
            return Response(
                {"detail": "Only the club owner can view members"},
                status=status.HTTP_403_FORBIDDEN,
            )
        members = club.memberships.all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
        
class MemberStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, club_pk, member_pk):
        club = get_object_or_404(Club, pk=club_pk)

        if request.user != club.owner:
            return Response (
                {"detail":"Only the club owner can approve or reject members."},
                status=status.HTTP_403_FORBIDDEN,
            )
        member=get_object_or_404(Member, pk=member_pk, club=club)

        new_status = request.data.get("status")
        if new_status not in [
            Member.STATUS_APPROVED,
            Member.STATUS_REJECTED,
        ]:
            return Response(
                {"detail":"Status must be approved or rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        member.status=new_status
        member.save()
        serializer = MemberSerializer(member)
        return Response(serializer.data)
