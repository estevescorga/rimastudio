(function(){
  "use strict";

  // Off-canvas menu
  var menuBtn = document.getElementById('menuBtn');
  var offcanvas = document.getElementById('offcanvas');
  var overlay = document.getElementById('offcanvasOverlay');
  var closeBtn = document.getElementById('offcanvasClose');

  function openMenu(){
    offcanvas.classList.add('open');
    overlay.classList.add('open');
  }
  function closeMenu(){
    offcanvas.classList.remove('open');
    overlay.classList.remove('open');
  }
  if (menuBtn) menuBtn.addEventListener('click', openMenu);
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  if (overlay) overlay.addEventListener('click', closeMenu);

  // Note: PT/EN are now separate static pages (/ and /en/), linked directly
  // in the markup — no client-side language toggle needed here anymore.

  // Header: on the home page it starts transparent over the hero photo and
  // turns opaque (.scrolled) once the page scrolls past it, so the nav stays
  // legible without permanently covering the hero image.
  var header = document.getElementById('siteHeader');
  if (header) {
    function onScroll(){
      if (window.scrollY > 40) header.classList.add('scrolled');
      else header.classList.remove('scrolled');
    }
    onScroll();
    window.addEventListener('scroll', onScroll, {passive:true});
  }

})();

// Contact form (Web3Forms)
(function(){
  var form = document.getElementById('contactForm');
  if (!form) return;
  var status = form.querySelector('.cf-status');
  var btn = form.querySelector('.cf-send');
  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    var fail = function(){
      status.textContent = form.dataset.err + ' ' + form.dataset.email;
    };
    if (!form.dataset.key) { fail(); return; }
    btn.disabled = true;
    status.textContent = '';
    var data = {};
    new FormData(form).forEach(function(v,k){ data[k] = v; });
    fetch('https://api.web3forms.com/submit', {
      method:'POST',
      headers:{'Content-Type':'application/json','Accept':'application/json'},
      body: JSON.stringify(data)
    }).then(function(r){ return r.json(); }).then(function(j){
      if (j && j.success) { status.textContent = form.dataset.ok; form.reset(); }
      else fail();
    }).catch(fail).then(function(){ btn.disabled = false; });
  });
})();

// Contact modal (The People Series)
(function(){
  var modal = document.getElementById('contactModal');
  if (!modal) return;
  function open(){ modal.hidden = false; document.body.style.overflow = 'hidden'; var i = modal.querySelector('input[type=text]'); if (i) i.focus(); }
  function close(){ modal.hidden = true; document.body.style.overflow = ''; }
  document.querySelectorAll('[data-open-contact]').forEach(function(b){ b.addEventListener('click', open); });
  modal.querySelectorAll('[data-close-contact]').forEach(function(b){ b.addEventListener('click', close); });
  modal.addEventListener('click', function(ev){ if (ev.target === modal) close(); });
  document.addEventListener('keydown', function(ev){ if (ev.key === 'Escape' && !modal.hidden) close(); });
})();

/* Project pages: video play buttons */
(function(){
  document.querySelectorAll('.pj-video').forEach(function(w){
    var v=w.querySelector('video'),b=w.querySelector('.pj-play');
    if(!v||!b)return;
    b.addEventListener('click',function(){
      document.querySelectorAll('.pj-video video').forEach(function(o){if(o!==v)o.pause();});
      v.controls=true;w.classList.add('is-playing');v.play();
    });
    v.addEventListener('ended',function(){v.controls=false;w.classList.remove('is-playing');});
  });
})();
