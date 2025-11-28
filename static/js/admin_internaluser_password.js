document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('id_new_password');
  const confirmInput = document.getElementById('id_confirm_password');
  const generateCheckbox = document.getElementById('id_generate_password');
  const statusMessage = document.createElement('div');
  statusMessage.className = 'password-status';

  const ensureStatus = () => {
    if (!passwordInput || !confirmInput) return;
    confirmInput.parentNode.appendChild(statusMessage);
  };

  const generateStrongPassword = () => {
    const length = 16;
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+[]{}|;:,.<>?';
    let str = '';
    for (let i = 0; i < length; i++) {
      str += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return str;
  };

  const updateStatus = () => {
    if (!passwordInput || !confirmInput) return;
    if (!confirmInput.value && !passwordInput.value) {
      statusMessage.textContent = '';
      statusMessage.classList.remove('status-ok', 'status-error');
      return;
    }
    if (passwordInput.value === confirmInput.value) {
      statusMessage.textContent = 'Senhas conferem.';
      statusMessage.classList.add('status-ok');
      statusMessage.classList.remove('status-error');
    } else {
      statusMessage.textContent = 'As senhas não coincidem.';
      statusMessage.classList.add('status-error');
      statusMessage.classList.remove('status-ok');
    }
  };

  const resetGeneratedFlag = () => {
    if (generateCheckbox && !generateCheckbox.checked) {
      confirmInput.value = '';
      if (statusMessage) {
        statusMessage.textContent = '';
        statusMessage.classList.remove('status-ok', 'status-error');
      }
    }
  };

  if (confirmInput && passwordInput) {
    ensureStatus();
    confirmInput.type = 'password';
    passwordInput.addEventListener('input', () => {
      if (generateCheckbox && generateCheckbox.checked) {
        confirmInput.value = passwordInput.value;
      }
      updateStatus();
    });
    confirmInput.addEventListener('input', () => {
      updateStatus();
    });
  }

  if (generateCheckbox) {
    generateCheckbox.addEventListener('change', () => {
      if (generateCheckbox.checked && passwordInput && confirmInput) {
        const generated = generateStrongPassword();
        passwordInput.value = generated;
        confirmInput.value = generated;
        updateStatus();
      } else {
        resetGeneratedFlag();
      }
    });
  }
});
