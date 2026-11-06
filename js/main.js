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

})();
