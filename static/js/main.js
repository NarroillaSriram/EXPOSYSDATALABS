// ===== PRELOADER & AOS INITIALIZATION =====
window.addEventListener('load', () => {
  const preloader = document.getElementById('preloader');
  if (preloader) {
    setTimeout(() => {
      preloader.style.opacity = '0';
      preloader.style.transition = 'opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
      setTimeout(() => {
        preloader.remove();
        if (typeof AOS !== 'undefined') {
          AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 50,
          });
        }
      }, 800);
    }, 600);
  } else if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      easing: 'ease-out-cubic',
      once: true,
      offset: 50,
    });
  }
});

// ===== SCROLL EFFECTS (NAVBAR, PROGRESS, BACK-TO-TOP) =====
window.addEventListener('scroll', () => {
  // Navbar
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    if (window.scrollY > 50) {
      navbar.style.padding = '8px 0';
      navbar.style.background = 'rgba(10, 36, 99, 0.98)';
      navbar.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
    } else {
      navbar.style.padding = '12px 0';
      navbar.style.background = 'rgba(10, 36, 99, 0.9)';
      navbar.style.boxShadow = 'none';
    }
  }

  // Scroll Progress
  const scrollBar = document.getElementById('scrollBar');
  if (scrollBar) {
    const scrollTotal = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (window.scrollY / scrollTotal) * 100;
    scrollBar.style.width = progress + '%';
  }

  // Back to top button
  const backToTop = document.getElementById('backToTop');
  if (backToTop) {
    if (window.scrollY > 300) {
      backToTop.classList.add('show');
    } else {
      backToTop.classList.remove('show');
    }
  }
});

// Back to top click
const backToTopBtn = document.getElementById('backToTop');
if (backToTopBtn) {
  backToTopBtn.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// ===== SMOOTH SCROLL =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ===== COUNTER ANIMATION =====
function animateCounter(el) {
  const target = parseInt(el.getAttribute('data-target'));
  const duration = 2500;
  let startTimestamp = null;
  const suffix = el.getAttribute('data-suffix') || '';

  const easeOutExpo = (t) => {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
  };

  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const easedProgress = easeOutExpo(progress);
    const current = Math.floor(easedProgress * target);
    
    el.textContent = current.toLocaleString() + suffix;
    
    if (progress < 1) {
      window.requestAnimationFrame(step);
    } else {
      el.textContent = target.toLocaleString() + suffix;
    }
  };
  window.requestAnimationFrame(step);
}

// ===== INTERSECTION OBSERVER =====
const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };

const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const animationClass = entry.target.getAttribute('data-animation') || 'fade-in';
      entry.target.classList.add(animationClass);
      fadeObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      counterObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.animate-on-scroll').forEach(el => fadeObserver.observe(el));
document.querySelectorAll('[data-target]').forEach(el => counterObserver.observe(el));

// ===== FLASH MESSAGE AUTO DISMISS =====
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(alert => {
    alert.style.transition = 'opacity 0.5s ease';
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 500);
  });
}, 4000);

// ===== MOBILE SIDEBAR TOGGLE =====
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.querySelector('.sidebar');
if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
}

// ===== PASSWORD TOGGLE (FONT AWESOME) =====
document.querySelectorAll('.password-toggle-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    const input = document.querySelector(this.getAttribute('data-pw-target'));
    const icon = this.querySelector('i');
    if (input && icon) {
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      } else {
        input.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      }
    }
  });
});

// ===== PAYMENT SCREENSHOT PREVIEW =====
const screenshotInput = document.getElementById('screenshot');
if (screenshotInput) {
  screenshotInput.addEventListener('change', function () {
    const preview = document.getElementById('screenshotPreview');
    if (preview && this.files[0]) {
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
      };
      reader.readAsDataURL(this.files[0]);
    }
  });
}

// ===== REGISTRATION FORM STEP VALIDATION =====
const regForm = document.getElementById('registrationForm');
if (regForm) {
  regForm.addEventListener('submit', function (e) {
    const password = document.getElementById('password');
    const confirm = document.getElementById('confirm_password');
    if (password && confirm && password.value !== confirm.value) {
      e.preventDefault();
      showAlert('Passwords do not match!', 'danger');
    }
  });
}

// ===== SEARCH TABLE =====
const searchInput = document.getElementById('tableSearch');
if (searchInput) {
  searchInput.addEventListener('input', function () {
    const query = this.value.toLowerCase();
    document.querySelectorAll('tbody tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
    });
  });
}

// ===== UTILITY: Show Alert =====
function showAlert(message, type = 'info') {
  const container = document.querySelector('.flash-container') || document.body;
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show`;
  alert.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  container.appendChild(alert);
  setTimeout(() => alert.remove(), 4000);
}

// ===== ACTIVE NAV LINK =====
const currentPath = window.location.pathname;
document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
  if (link.getAttribute('href') === currentPath) {
    link.classList.add('active');
  }
});

// ===== MOUSE GLOW EFFECT =====
const mouseGlow = document.querySelector('.mouse-glow');
if (mouseGlow) {
  document.addEventListener('mousemove', (e) => {
    mouseGlow.style.opacity = '1';
    mouseGlow.style.left = e.clientX + 'px';
    mouseGlow.style.top = e.clientY + 'px';
  });
  
  document.addEventListener('mouseleave', () => {
    mouseGlow.style.opacity = '0';
  });
}
