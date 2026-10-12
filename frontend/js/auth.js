/* TAMALE HOUSE MARKET - PostgreSQL-backed authentication via the REST API. */

document.addEventListener('DOMContentLoaded', () => {
  initLoginForm();
  initRegisterForm();
});

function backendUnavailable(response) {
  return !response || response.status === 404 || response.status === 405;
}

function unavailableMessage(response, action) {
  if (!response) {
    return `Cannot reach the ${action} API. Start the Flask server and check its PostgreSQL configuration.`;
  }
  return `The ${action} API route was not found. Open the site served by Flask at http://localhost:5000.`;
}

async function postJSON(url, body) {
  try {
    return await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
  } catch (e) {
    return null; // network failure
  }
}

function initLoginForm() {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) return;

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const usernameInput = document.getElementById('login-username').value.trim();
    const passwordInput = document.getElementById('login-password').value;
    const errorBox = document.getElementById('login-error');
    if (errorBox) errorBox.style.display = 'none';

    if (!usernameInput || !passwordInput) {
      showAuthError(errorBox, 'Please enter both username/email and password.');
      return;
    }

    const response = await postJSON('/api/auth/login', { username: usernameInput, password: passwordInput });

    if (response && response.ok) {
      const user = await response.json();
      setCurrentUser(user);
      redirectUserDashboard(user.role);
      return;
    }

    if (response && !backendUnavailable(response)) {
      const errorData = await response.json().catch(() => ({}));
      showAuthError(errorBox, errorData.error || 'Invalid username or password.');
      return;
    }
    showAuthError(errorBox, unavailableMessage(response, 'authentication'));
  });
}

function initRegisterForm() {
  const registerForm = document.getElementById('register-form');
  if (!registerForm) return;

  const landlordRoleCard = document.getElementById('role-landlord');
  const tenantRoleCard = document.getElementById('role-tenant');
  const roleInput = document.getElementById('register-role');

  if (landlordRoleCard && tenantRoleCard && roleInput) {
    landlordRoleCard.addEventListener('click', () => {
      landlordRoleCard.classList.add('selected-role');
      tenantRoleCard.classList.remove('selected-role');
      roleInput.value = 'landlord';
    });
    tenantRoleCard.addEventListener('click', () => {
      tenantRoleCard.classList.add('selected-role');
      landlordRoleCard.classList.remove('selected-role');
      roleInput.value = 'tenant';
    });
  }

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fullName = document.getElementById('reg-fullname').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;
    const role = roleInput ? roleInput.value : '';
    const errorBox = document.getElementById('register-error');
    if (errorBox) errorBox.style.display = 'none';

    if (!fullName || !email || !username || !password || !confirmPassword) {
      showAuthError(errorBox, 'Please complete all required registration fields.');
      return;
    }
    if (role !== 'landlord' && role !== 'tenant') {
      showAuthError(errorBox, 'Please choose your account role: LANDLORD or TENANT.');
      return;
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      showAuthError(errorBox, 'Please enter a valid email address.');
      return;
    }
    if (password !== confirmPassword) {
      showAuthError(errorBox, 'Passwords do not match. Please re-enter.');
      return;
    }
    if (password.length < 8) {
      showAuthError(errorBox, 'Password must be at least 8 characters long.');
      return;
    }

    const response = await postJSON('/api/auth/register', { username, email, password, role, full_name: fullName });

    // Backend handled it: never store credentials locally
    if (response && response.ok) {
      const created = await response.json().catch(() => null);
      const user = created && created.role ? created : { username, full_name: fullName, email, role };
      setCurrentUser(user);
      redirectUserDashboard(user.role);
      return;
    }

    if (response && !backendUnavailable(response)) {
      const errorData = await response.json().catch(() => ({}));
      showAuthError(errorBox, errorData.error || 'Registration failed. Username or Email already exists.');
      return;
    }

    showAuthError(errorBox, unavailableMessage(response, 'registration'));
  });
}

function showAuthError(errorBox, message) {
  if (!errorBox) return;
  errorBox.style.display = 'block';
  errorBox.textContent = message;
}

function redirectUserDashboard(role) {
  window.location.href = role === 'landlord' ? 'landlord/dashboard.html' : 'tenant/dashboard.html';
}
