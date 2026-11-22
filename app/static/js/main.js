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

  // Admission form: show the fixed days and timing for the chosen class type
  var schedule = document.getElementById('schedule');
  if (schedule) {
    var showSchedule = function () {
      var chosen = document.querySelector('input[name="mode"]:checked');
      var text = chosen && schedule.getAttribute('data-' + chosen.value.toLowerCase());
      if (text) { schedule.textContent = chosen.value + ' classes: ' + text; schedule.classList.add('on'); }
    };
    document.querySelectorAll('input[name="mode"]').forEach(function (r) { r.addEventListener('change', showSchedule); });
    showSchedule();
  }