/* ═══════════════════════════════════════════════════════════════════════
   COURSIFY — Main JavaScript
   Handles auth state, API calls, UI interactions, and dynamic content
   ═══════════════════════════════════════════════════════════════════════ */

// ─── Auth State Management ─────────────────────────────────────────────
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    
    const authButtons = document.getElementById('authButtons');
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');

    if (token && user && authButtons && userMenu) {
        authButtons.style.display = 'none';
        userMenu.style.display = 'flex';
        userName.textContent = user.first_name || user.username;
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

async function refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return null;

    try {
        const response = await fetch('/api/accounts/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            if (data.refresh) {
                localStorage.setItem('refresh_token', data.refresh);
            }
            return data.access;
        } else {
            logout();
            return null;
        }
    } catch {
        return null;
    }
}

async function authFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login/';
        return;
    }

    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
    };

    let response = await fetch(url, options);

    // If 401, try refreshing token
    if (response.status === 401) {
        token = await refreshToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
            response = await fetch(url, options);
        }
    }

    return response;
}

// ─── Navigation ─────────────────────────────────────────────────────────
function toggleNav() {
    document.getElementById('navLinks')?.classList.toggle('open');
    document.getElementById('navActions')?.classList.toggle('open');
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
});

// ─── Toast Notification ─────────────────────────────────────────────────
function showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

// ─── Course Card Generator ──────────────────────────────────────────────
function createCourseCard(course) {
    const price = parseFloat(course.price || 0);
    const priceText = price === 0 ? 'Free' : `$${price.toFixed(2)}`;
    const priceClass = price === 0 ? 'course-price free' : 'course-price';
    const badgeClass = price === 0 ? 'card-badge free' : 'card-badge';
    const badgeText = price === 0 ? 'Free' : course.category;

    const thumbnail = course.thumbnail
        ? `<img src="${course.thumbnail}" alt="${course.title}" class="card-img">`
        : `<div class="card-img" style="background: linear-gradient(135deg, var(--primary-200), var(--primary-400)); display: flex; align-items: center; justify-content: center; font-size: 3rem;">🎓</div>`;

    return `
        <div class="card course-card animate-in">
            <div style="position: relative;">
                <span class="${badgeClass}">${badgeText}</span>
                ${thumbnail}
            </div>
            <div class="card-body">
                <div class="course-meta">
                    <span class="star-rating">⭐ ${course.average_rating || '0.0'}</span>
                    <span>📚 ${course.total_lessons || 0} lessons</span>
                </div>
                <h3 class="card-title">${course.title}</h3>
                <p class="card-text">${course.description || ''}</p>
                <div class="course-instructor">
                    <div style="width: 28px; height: 28px; border-radius: 50%; background: var(--primary-200); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; color: var(--primary-700);">
                        ${(course.instructor_name || 'I').charAt(0).toUpperCase()}
                    </div>
                    <span style="color: var(--gray-600);">${course.instructor_name || 'Instructor'}</span>
                </div>
            </div>
            <div class="card-footer">
                <span class="${priceClass}">${priceText}</span>
                <a href="/courses/${course.slug}/" class="btn btn-primary btn-sm">View Course</a>
            </div>
        </div>
    `;
}

// ─── Scroll Animations ─────────────────────────────────────────────────
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// ─── Initialize ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();

    // Observe animate-in elements
    document.querySelectorAll('.animate-in').forEach(el => {
        observer.observe(el);
    });
});
