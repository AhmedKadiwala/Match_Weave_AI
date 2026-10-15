/** Paste this file into a standalone project at script.google.com. Set your real URL below. */
const BACKEND_URL = 'https://YOUR-ACTUAL-BACKEND.onrender.com';

/** Set a Time-driven > Minutes timer > Every 5 minutes trigger for this function. */
function pingBackend() {
  if (!/^https:\/\/[^/?#]+\.onrender\.com\/?$/.test(BACKEND_URL) || BACKEND_URL.indexOf('YOUR-') !== -1) {
    throw new Error('Replace BACKEND_URL with the real https://...onrender.com origin first.');
  }
  const url = BACKEND_URL.replace(/\/+$/, '') + '/api/health';
  const response = UrlFetchApp.fetch(url, {
    method: 'get',
    followRedirects: true,
    muteHttpExceptions: true,
    headers: {'Cache-Control': 'no-cache', 'X-MatchWeave-Ping': 'google-apps-script'}
  });
  const status = response.getResponseCode();
  if (status !== 200) {
    throw new Error('Backend health returned HTTP ' + status + '. Check Render logs or retry after cold start.');
  }
  let health;
  try { health = JSON.parse(response.getContentText()); }
  catch (_) { throw new Error('Health response was not JSON. The service may still be waking up.'); }
  if (health.status !== 'ok') throw new Error('Backend did not report healthy status.');
  const result = {checkedAt: new Date().toISOString(), status: status, deployment: health.deployment || 'unknown'};
  console.log(JSON.stringify(result));
  return result;
}
