/**
 * AirIQ — Main JavaScript
 * Global UI enhancements
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss flash alerts after 5 s ──
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  // ── Navbar scroll effect ──
  const nav = document.getElementById('mainNav');
  if (nav) {
    const handler = () => {
      nav.style.boxShadow = window.scrollY > 10
        ? '0 4px 24px rgba(0,0,0,0.5)'
        : 'none';
    };
    window.addEventListener('scroll', handler, { passive: true });
  }

  // ── Animate elements on scroll ──
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity    = '1';
        entry.target.style.transform  = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.feature-card, .aqi-card, .pollutant-card, .tech-card, .detail-card').forEach(el => {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

});