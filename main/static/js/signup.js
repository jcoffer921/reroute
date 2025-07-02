document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.querySelector('#id_password');
    const strengthText = document.getElementById('password-strength');

    if (passwordInput && strengthText) {
        passwordInput.addEventListener('input', function () {
            const val = passwordInput.value;
            let strength = 0;

            if (val.length >= 8) strength++;
            if (/[A-Z]/.test(val)) strength++;
            if (/[a-z]/.test(val)) strength++;
            if (/\d/.test(val)) strength++;
            if (/[!@#$%^&*(),.?":{}|<>]/.test(val)) strength++;

            switch (strength) {
                case 0:
                case 1:
                    strengthText.textContent = 'Very weak';
                    strengthText.style.color = 'red';
                    break;
                case 2:
                case 3:
                    strengthText.textContent = 'Medium strength';
                    strengthText.style.color = 'orange';
                    break;
                case 4:
                case 5:
                    strengthText.textContent = 'Strong password';
                    strengthText.style.color = 'green';
                    break;
            }
        });
    }
});
