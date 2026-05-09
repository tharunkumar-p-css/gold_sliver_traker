// AJAX toggle for enabling/disabling alerts without reloading the page
async function toggleAlert(alertId, checkbox) {
  const card = document.getElementById(`alertCard${alertId}`);
  const cardDiv = card.querySelector('.alert-card');
  const originalState = !checkbox.checked;

  try {
    const csrfToken = getCookie('csrftoken');
    const response = await fetch(`/alerts/${alertId}/toggle/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      if (data.is_active) {
        cardDiv.classList.remove('alert-card-inactive');
      } else {
        cardDiv.classList.add('alert-card-inactive');
      }
    } else {
      // Revert if failed
      checkbox.checked = originalState;
      showToast('Error toggling alert status.', 'error');
    }
  } catch (error) {
    console.error('Toggle error:', error);
    checkbox.checked = originalState;
    showToast('Network error while toggling alert.', 'error');
  }
}

// Utility to get Django CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Minimal toast notification for JS errors
function showToast(msg, type='info') {
  const container = document.querySelector('.messages-container') || createToastContainer();
  const id = 'toast' + Date.now();
  const icon = type === 'error' ? 'x-circle' : 'info-circle';

  const html = `
    <div class="alert-toast alert-toast-${type}" id="${id}">
      <i class="bi bi-${icon}"></i>
      ${msg}
      <button type="button" class="toast-close" onclick="this.parentElement.remove()">×</button>
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);
  setTimeout(() => {
    const el = document.getElementById(id);
    if (el) el.remove();
  }, 5000);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.className = 'messages-container';
  document.body.appendChild(div);
  return div;
}
