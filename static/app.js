const form = document.querySelector('#lead-form');
const phone = form.elements.phone;
const statusBox = form.querySelector('.form-status');
const phonePattern = /^(?:\+375|80)\s*\(?\d{2}\)?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}$/;
let sending = false;
let conversionSource = 'direct_form';
phone.addEventListener('input', () => { phone.setCustomValidity(''); phone.classList.remove('invalid'); });
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (sending) return;
  const data = new FormData(form);
  const digits = String(data.get('phone')).replace(/\D/g, '');
  if (!phonePattern.test(String(data.get('phone')).trim())) {
    phone.setCustomValidity('Введите белорусский номер, например +375 29 123-45-67.'); phone.reportValidity(); phone.classList.add('invalid'); return;
  }
  const params = new URLSearchParams(location.search);
  const payload = Object.fromEntries(data.entries());
  payload.source = conversionSource;
  for (const key of ['utm_source','utm_medium','utm_campaign','utm_content','utm_term']) payload[key] = params.get(key) || '';
  payload.landing = location.href; payload.referrer = document.referrer || '';
  // Ignore a fast repeat on this device; the server also enforces the 10 minute window across sessions.
  const cacheKey = `kvarta:${digits.slice(-9)}`;
  const lastSent = Number(sessionStorage.getItem(cacheKey) || 0);
  if (Date.now() - lastSent < 600000) { statusBox.textContent = 'Мы уже получили заявку с этого номера. Скоро вам позвоним.'; statusBox.className = 'form-status error'; return; }
  sending = true; form.querySelector('button').disabled = true; form.querySelector('.button-label').textContent = 'Отправляем…'; statusBox.textContent = '';
  try {
    const response = await fetch('/api/lead', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Не удалось отправить заявку. Позвоните нам по номеру +375 29 123-45-67.');
    sessionStorage.setItem(cacheKey, String(Date.now())); form.reset(); statusBox.textContent = result.message; statusBox.className = 'form-status success';
  } catch (error) { statusBox.textContent = error.message || 'Нет соединения. Позвоните нам: +375 29 123-45-67.'; statusBox.className = 'form-status error'; }
  finally { sending = false; form.querySelector('button').disabled = false; form.querySelector('.button-label').textContent = 'Отправить заявку'; }
});
document.querySelectorAll('[data-interest]').forEach(link => link.addEventListener('click', () => { form.elements.interest.value = link.dataset.interest; }));
document.querySelectorAll('[data-lead-source]').forEach(link => link.addEventListener('click', () => { conversionSource = link.dataset.leadSource; }));
