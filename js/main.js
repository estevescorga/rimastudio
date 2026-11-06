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
