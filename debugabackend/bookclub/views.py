import json
# URL-encode query params and API key for the Google Books request.
from urllib.parse import quote_plus
# Raised when Google Books API returns 4xx/5xx (e.g. 429 quota exceeded).
from urllib.error import HTTPError
# Fetch the Google Books API response; URLError for network/connection failures.
from urllib.request import urlopen, URLError
from django.db.models import Count

# GOOGLE_BOOKS_API_KEY is read from here for the BookSearch proxy.
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Meeting, AnnouncementThread, Club, Member, ClubBook
from .serializers import (ClubSerializer, MeetingSerializer,AnnouncementThreadSerializer, MemberSerializer, MeetingAttendanceSerializer, ClubBookSerializer, HomeStatsSerializer)


#fuction to centralise club visibility rule
#general club details visible to everyone, but meetings/announcement restricted to only owner and member
def is_club_owner(user,club):
    return user.is_authenticated and user == club.owner

def is_approved_member(user, club):
    if not user.is_authenticated:
        return False
    return Member.objects.filter(
        club=club,
        user=user,
        status=Member.STATUS_APPROVED,).exists()

def can_view_member_content(user, club):
    return is_club_owner(user,club) or is_approved_member(user,club)


class ClubListCreate(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        clubs = Club.objects.filter(is_active=True)
        serializer = ClubSerializer(clubs, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ClubSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#get individual clubs   
class ClubDetail(APIView):
    def get_permissions(self):
        if self.request.method == ("PUT", "PATCH"):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, pk):
        club = get_object_or_404(Club, pk=pk, is_active=True)
        serializer = ClubSerializer(club, context={"request": request})
        return Response(serializer.data)
    
    def patch(self, request, pk):
        club = get_object_or_404(Club, pk=pk)

        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can edit this club."},
                status=status.HTTP_403_FORBIDDEN,
             )

        serializer = ClubSerializer(
            club,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        club = get_object_or_404(Club, pk=pk)
        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can delete this club."},
                status=status.HTTP_403_FORBIDDEN,
             )
        
        club.is_active = False
        club.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
    
class MeetingListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        if not can_view_member_content(request.user, club):
            return Response(
                {"detail": "You don't have permissions to view this content."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        meetings = Meeting.objects.filter(club=club)
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

class MeetingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id, meeting_id):
        club = get_object_or_404(Club, pk=club_id)
        meeting = get_object_or_404(Meeting, pk=meeting_id, club=club)
        if not can_view_member_content(request.user, club):
            return Response(
                {"detail": "You don't have permissions to view this meeting."},
                status=status.HTTP_403_FORBIDDEN,
            )   
        serializer = MeetingSerializer(meeting, context={"request": request})
        return Response(serializer.data)
    
    def patch(self, request, club_id, meeting_id):
        club = get_object_or_404(Club, pk=club_id)
        meeting = get_object_or_404(Meeting, pk=meeting_id, club=club)

        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can edit meeetings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = MeetingSerializer(meeting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, club_id, meeting_id):
        club = get_object_or_404(Club, pk=club_id)
        meeting = get_object_or_404(Meeting, pk=meeting_id, club=club)

        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can delete meetings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if meeting.attendance.exists():
            return Response(
                {"detail": "You cannot delete a meeting that already has bookings."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

class MeetingAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)

        if request.user == meeting.club.owner:
            return Response(
                {"detail":"Club owner does not need to book a meeting."},
                status=status.HTTP_400_BAD_REQUEST,
            )   
        # 1. User needs to be member of the club
        member = Member.objects.filter(
            user=request.user, 
            club=meeting.club, 
            status=Member.STATUS_APPROVED
        ).first()

        if not member:
            return Response(
                {"detail": "You must be an approved member of this club to join the meeting."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2.Creation and duplicate check
        serializer = MeetingAttendanceSerializer(data={'meeting': meeting.id, 'member': member.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"detail": "You're booked for this meeting!"}, status=status.HTTP_201_CREATED)

class AnnouncementListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)

        if not can_view_member_content(request.user, club):
            return Response(
                {"detail": "You don't have permissions to view announcements."},
                status=status.HTTP_403_FORBIDDEN,
            )

        announcements = AnnouncementThread.objects.filter(club=club)
        serializer = AnnouncementThreadSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)

        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can post announcements."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AnnouncementThreadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(club=club)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#Announcement can be edited, but not deleted. So, only Get/pacth announcement is set    
class AnnouncementDetailView(APIView):
    permission_classes= [IsAuthenticated]

    def get(self, request, club_id, announcementthread_id):
        club = get_object_or_404(Club, pk=club_id)
        announcement = get_object_or_404(AnnouncementThread, pk=announcementthread_id, club=club)

        if not can_view_member_content(request.user, club):
            return Response(
                {"detail": "You don't have permissions to view this announcement."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AnnouncementThreadSerializer(announcement, context={"request": request})
        return Response(serializer.data)
    
    def patch(self, request, club_id, announcementthread_id):
        club = get_object_or_404(Club, pk=club_id)
        announcement = get_object_or_404(AnnouncementThread, pk=announcementthread_id, club=club)

        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can edit announcements."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AnnouncementThreadSerializer(announcement, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(club=club)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClubBookListCreateView(APIView):
        def get_permissions(self):
            if self.request.method == "POST":
                return [IsAuthenticated()]
            return [AllowAny()]
        
        def get(self, request, club_id):
            club = get_object_or_404(Club, pk=club_id)
            books = ClubBook.objects.filter(club=club)
            serializer = ClubBookSerializer(books, many=True, context={"request": request})
            return Response(serializer.data)
            
        def post(self, request, club_id):
            club=get_object_or_404(Club, pk=club_id)

            if request.user != club.owner:
                return Response(
                    {"detail": "Only the owner can add books."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = ClubBookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(club=club)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class ClubBookDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, club_id, book_id):
        club = get_object_or_404(Club, pk=club_id)
        book = get_object_or_404(ClubBook, pk=book_id, club=club)
        serializer = ClubBookSerializer(book, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, club_id, book_id):
        club = get_object_or_404(Club, pk=club_id)
        book = get_object_or_404(ClubBook, pk=book_id, club=club)

        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can edit books."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ClubBookSerializer(book, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, club_id, book_id):
        club = get_object_or_404(Club, pk=club_id)
        book = get_object_or_404(ClubBook, pk=book_id, club=club)

        if request.user != club.owner:
            return Response(
                {"detail": "Only the owner can delete books."},
                status=status.HTTP_403_FORBIDDEN,
            )

        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class BookSearch(APIView):
    """Proxy to Google Books API. Requires GOOGLE_BOOKS_API_KEY in env."""
    permission_classes = [IsAuthenticated]

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
            identifiers = vi.get("industryIdentifiers") or []
            categories = vi.get("categories") or []

            isbn = ""
            for identifier in identifiers:
                 if identifier.get("type") == "ISBN_13":
                    isbn = identifier.get("identifier", "")
                    break

            if not isbn:
                  for identifier in identifiers:
                      if identifier.get("type") == "ISBN_10":
                        isbn = identifier.get("identifier", "")
                        break

            results.append({
                "google_books_id": item.get("id"),
                "title": vi.get("title") or "Untitled",
                "author": ", ".join(vi.get("authors") or ["Unknown author"]),
                "description": vi.get("description") or "",
                "cover_image": links.get("thumbnail") or links.get("smallThumbnail") or "",
                "isbn": isbn,
                "genre": ", ".join(categories) if categories else "",
            })
        return Response(results, status=status.HTTP_200_OK)
    
class HomeStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        active_readers = (
            Members.objects.filter(status=Member.STATUS_APPROVED, club__is_active=True)
            .values("user")
            .distinct()
            .count()
        )
        total_books_read = ClubBook.objects.filter(
            status=ClubBook.STATUS_READ,
            club__is_active=True,
        ).count()

        data = {
            "active_readers": active_readers,
            "total_books_read": total_books_read,
        }

        serializer = HomeStatsSerializer(data)
        return Response(serializer.data)