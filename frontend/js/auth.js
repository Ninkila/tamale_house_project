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

    if (errorBox) errorBox.style.display = 'none';

    if (!usernameInput || !passwordInput) {
      showAuthError(errorBox, 'Please enter both username/email and password.');
      return;
    }

    // Attempt Backend REST API Authentication
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
      } else {
        const errorData = await response.json().catch(() => ({}));
        showAuthError(errorBox, errorData.error || 'Invalid username or password.');
        return;
      }
    } catch (err) {
      // Backend server not reachable - check client-side registered users with strict password match
      const localUsers = JSON.parse(localStorage.getItem('thm_users') || '[]');
      const foundUser = localUsers.find(
        u => (u.username.toLowerCase() === usernameInput.toLowerCase() || u.email.toLowerCase() === usernameInput.toLowerCase()) && u.password === passwordInput
      );

      if (foundUser) {
        const { password, ...safeUser } = foundUser;
        setCurrentUser(safeUser);
        redirectUserDashboard(foundUser.role);
        return;
      }

      showAuthError(errorBox, 'Invalid username or password. Please register an account first.');
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
    const role = roleInput ? roleInput.value : '';
    const errorBox = document.getElementById('register-error');

    if (errorBox) errorBox.style.display = 'none';

    if (!fullName || !email || !username || !password || !confirmPassword) {
      showAuthError(errorBox, 'Please complete all required registration fields.');
      return;
    }

    if (!role || (role !== 'landlord' && role !== 'tenant')) {
      showAuthError(errorBox, 'Please choose your account role: LANDLORD or TENANT.');
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

    // Check local existing registration
    const localUsers = JSON.parse(localStorage.getItem('thm_users') || '[]');
    if (localUsers.some(u => u.username.toLowerCase() === username.toLowerCase() || u.email.toLowerCase() === email.toLowerCase())) {
      showAuthError(errorBox, 'Username or email address is already registered.');
      return;
    }

    // Attempt Backend REST API registration
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, role, full_name: fullName })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        showAuthError(errorBox, errorData.error || 'Registration failed. Username or Email already exists.');
        return;
      }
    } catch (err) {
      // Offline / standalone local fallback
    }

    const newUser = {
      username: username,
      full_name: fullName,
      email: email,
      password: password,
      role: role
    };

    localUsers.push(newUser);
    localStorage.setItem('thm_users', JSON.stringify(localUsers));

    // Log in authenticated user with chosen role
    const { password: _, ...loggedUser } = newUser;
    setCurrentUser(loggedUser);
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
