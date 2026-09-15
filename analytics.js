/* Site-wide visitor counting for craigsingleton.org via GoatCounter.
 *
 * GoatCounter is free for personal/non-commercial sites, sets no cookies, and
 * needs no consent banner. Dashboard: https://<code>.goatcounter.com
 *
 * ONE-TIME SETUP: sign up at https://www.goatcounter.com/signup, pick a site
 * code (e.g. "craigsingleton"), and put it in GOATCOUNTER_CODE below. Until the
 * code is filled in this file does nothing.
 */
(function () {
  var GOATCOUNTER_CODE = '';

  if (!GOATCOUNTER_CODE) return;
  var host = location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '') return;

  var endpoint = 'https://' + GOATCOUNTER_CODE + '.goatcounter.com/count';
  window.goatcounter = window.goatcounter || {};
  window.goatcounter.endpoint = endpoint;
  // Spaces in two page names are %20-encoded in URLs; report them readably.
  window.goatcounter.path = function (p) { try { return decodeURIComponent(p); } catch (e) { return p; } };

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://gc.zgo.at/count.js';
  s.setAttribute('data-goatcounter', endpoint);
  document.head.appendChild(s);
})();
