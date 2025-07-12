// login.js

// 🔐 Helper: Extract CSRF token from cookie
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length);
        }
    }
    return '';
}

// 🚀 Main login submission function
async function submitLogin(event) {
    event.preventDefault(); // prevent default form submission

    const username = document.getElementById('id_username').value;
    const password = document.getElementById('id_password').value;

    try {
        const response = await fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Login success:', data);
            window.location.href = data.redirect || '/dashboard/';  // update to your success redirect
        } else {
            const errorData = await response.json();
            console.error('Login failed:', errorData);
            document.getElementById('login-error').textContent = errorData.message || 'Login failed.';
        }
    } catch (error) {
        console.error('Unexpected error:', error);
        document.getElementById('login-error').textContent = 'Something went wrong.';
    }
}

// 📎 Attach handler to form on DOM load
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', submitLogin);
    }
});
