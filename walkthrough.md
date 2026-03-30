# Coursify — Build Walkthrough

## What Was Built

A production-ready Online Course Platform with:

### Backend (Django + DRF)
- **5 Django apps**: `accounts`, [courses](file:///c:/Users/ritar/OneDrive/Desktop/Django%20Projects/Coursify/accounts/serializers.py#54-58), `enrollments`, `quizzes`, `reviews`
- **JWT Authentication** via SimpleJWT (register, login, token refresh)
- **Role-based permissions** (Student, Instructor, Admin)
- **18 models** total across all apps
- **Full REST API** with ViewSets, search, filtering, pagination, and throttling

### Frontend (Django Templates)
- **7 pages**: Home, Login, Register, Course Catalog, Course Detail, Student Dashboard, Instructor Dashboard
- **Green theme** inspired by reference design (`#16a34a` primary)
- **1000+ lines of CSS** with design tokens, animations, responsive grid
- **Dynamic content** loaded via JavaScript API calls

---

## Project Structure

```
Coursify/
├── coursify/          # Django project config
│   ├── settings.py    # JWT, DRF, CORS, pagination, throttling
│   └── urls.py        # Main URL routing
├── accounts/          # User auth, profiles, dashboards
├── courses/           # Course, Section, Lesson, Bookmark, Wishlist
├── enrollments/       # Enrollment, LessonProgress, Certificate
├── quizzes/           # Quiz, Question, Option, QuizAttempt
├── reviews/           # Course reviews & ratings
├── templates/         # Green-themed HTML templates
├── static/css/        # Design system (style.css)
├── static/js/         # Client-side logic (main.js)
└── manage.py
```

---

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/register/` | Register + get JWT tokens |
| POST | `/api/accounts/login/` | Login + get JWT tokens |
| POST | `/api/accounts/token/refresh/` | Refresh access token |
| GET | `/api/accounts/profile/` | View/update profile |
| GET | `/api/accounts/dashboard/student/` | Student stats |
| GET | `/api/accounts/dashboard/instructor/` | Instructor stats |
| GET/POST | `/api/courses/` | List/create courses |
| GET | `/api/courses/{slug}/` | Course detail with sections |
| POST | `/api/courses/{slug}/publish/` | Toggle publish |
| GET/POST | `/api/enrollments/` | List/create enrollments |
| POST | `/api/lesson-progress/` | Track lesson progress |
| GET/POST | `/api/quizzes/` | Manage quizzes |
| POST | `/api/quizzes/{id}/submit/` | Submit & auto-grade quiz |
| GET/POST | `/api/reviews/` | Course reviews |
| GET/POST | `/api/bookmarks/` | Bookmark lessons |
| GET/POST | `/api/wishlist/` | Wishlist courses |

---

## Verification Results

| Check | Result |
|-------|--------|
| `python manage.py check` | ✅ 0 issues |
| `python manage.py makemigrations` | ✅ All 5 apps |
| `python manage.py migrate` | ✅ All applied |
| `python manage.py runserver` | ✅ Running on port 8000 |
| Home page (`/`) | ✅ 200 OK — 13,947 bytes |
| Login (`/login/`) | ✅ 200 OK |
| Register (`/register/`) | ✅ 200 OK |
| Dashboard (`/dashboard/`) | ✅ 200 OK |
| Instructor (`/instructor/`) | ✅ 200 OK |
| API endpoints | ✅ All returning 200 |

---

## How to Run

```bash
cd "c:\Users\ritar\OneDrive\Desktop\Django Projects\Coursify"
python manage.py runserver 8000
```

Then open `http://localhost:8000/` in your browser.
