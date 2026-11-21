(function () {
  // Mobile menu
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  // Prevent double submits and flag invalid fields for assistive tech
  document.querySelectorAll('form[data-once]').forEach(function (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn && form.checkValidity()) { btn.disabled = true; btn.textContent = 'Sending...'; }
    });
    form.addEventListener('invalid', function (e) { e.target.setAttribute('aria-invalid', 'true'); }, true);
    form.addEventListener('input', function (e) { e.target.removeAttribute('aria-invalid'); });
  });
})();
