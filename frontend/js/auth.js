/* ==========================================================================
   TAMALE HOUSE MARKET - AUTHENTICATION MODULE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initLoginForm();
  initRegisterForm();
});

// LOGIN HANDLING
function initLoginForm() {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) return;

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const usernameInput = document.getElementById('login-username').value.trim();
    const passwordInput = document.getElementById('login-password').value;
    const errorBox = document.getElementById('login-error');

    if (!usernameInput || !passwordInput) {
      showAuthError(errorBox, 'Please enter both username/email and password.');
      return;
    }

    // Check backend API or prototype local storage fallback
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput, password: passwordInput })
      });

      if (response.ok) {
        const user = await response.json();
        setCurrentUser(user);
        redirectUserDashboard(user.role);
        return;
      }
    } catch (err) {
      // Prototype Fallback Login
    }

    // Check local registered users fallback
    const localUsers = JSON.parse(localStorage.getItem('thm_users') || '[]');
    const foundUser = localUsers.find(u => (u.username === usernameInput || u.email === usernameInput));

    if (foundUser) {
      setCurrentUser(foundUser);
      redirectUserDashboard(foundUser.role);
      return;
    }

    // Default prototype login for test credentials
    if (usernameInput.toLowerCase().includes('landlord')) {
      const user = { username: usernameInput, full_name: 'Landlord User', email: 'landlord@tamalehouse.com', role: 'landlord' };
      setCurrentUser(user);
      redirectUserDashboard('landlord');
    } else {
      const user = { username: usernameInput, full_name: 'Tenant User', email: 'tenant@tamalehouse.com', role: 'tenant' };
      setCurrentUser(user);
      redirectUserDashboard('tenant');
    }
  });
}

// REGISTER HANDLING
function initRegisterForm() {
  const registerForm = document.getElementById('register-form');
  if (!registerForm) return;

  // Role Selection Cards
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
    const role = roleInput ? roleInput.value : 'tenant';
    const errorBox = document.getElementById('register-error');

    if (!fullName || !email || !username || !password || !confirmPassword) {
      showAuthError(errorBox, 'Please complete all required fields.');
      return;
    }

    if (password !== confirmPassword) {
      showAuthError(errorBox, 'Passwords do not match. Please re-enter.');
      return;
    }

    if (password.length < 6) {
      showAuthError(errorBox, 'Password must be at least 6 characters long.');
      return;
    }

    const newUser = {
      username: username,
      full_name: fullName,
      email: email,
      role: role
    };

    // Save locally
    const localUsers = JSON.parse(localStorage.getItem('thm_users') || '[]');
    if (localUsers.some(u => u.username === username || u.email === email)) {
      showAuthError(errorBox, 'Username or Email is already registered.');
      return;
    }

    localUsers.push(newUser);
    localStorage.setItem('thm_users', JSON.stringify(localUsers));

    // Try backend API registration
    try {
      await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, role, full_name: fullName })
      });
    } catch (err) {}

    // Auto log in user
    setCurrentUser(newUser);
    redirectUserDashboard(role);
  });
}

function showAuthError(errorBox, message) {
  if (!errorBox) return;
  errorBox.style.display = 'block';
  errorBox.textContent = message;
}

function redirectUserDashboard(role) {
  if (role === 'landlord') {
    window.location.href = 'landlord/dashboard.html';
  } else {
    window.location.href = 'tenant/dashboard.html';
  }
}
