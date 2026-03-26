"""
Curated genre labels for club multi-select (matches the app's fiction, nonfiction,
and TV-style category lists). Used for validation and GET /books/categories/.
"""

# Maximum genres a club may select (enforced in ClubSerializer and frontend).
MAX_CLUB_GENRES = 10

# Ordered: fiction → nonfiction → TV / streaming-style (deduplicated labels).
BOOK_CATEGORIES = [
    # Fiction genres
    "Children's Fiction",
    "Classics",
    "Cozy Fantasy",
    "Dark Romance",
    "Fantasy",
    "Graphic Novels",
    "Historical Fiction",
    "Horror",
    "LGBTQ+",
    "Literary Fiction",
    "Manga",
    "Mystery",
    "Poetry",
    "Romance",
    "Sci-Fi",
    "Sci-Fi & Fantasy",
    "Short Stories",
    "Thrillers",
    "Young Adult",
    # Nonfiction genres
    "Art & Design",
    "Biography",
    "Business",
    "Education",
    "Food",
    "History",
    "Humor",
    "Music",
    "Nature & Environment",
    "Personal Growth",
    "Politics",
    "Psychology",
    "Religion & Spirituality",
    "Science & Technology",
    "Sports",
    "Travel",
    "True Crime",
    "Wellness",
    # TV show / streaming genres
    "Action & Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Kids",
    "Musical",
    "News",
    "Reality",
    "Soap",
    "Talk",
    "War & Politics",
    "Western",
]

ALLOWED_BOOK_CATEGORIES = frozenset(BOOK_CATEGORIES)
