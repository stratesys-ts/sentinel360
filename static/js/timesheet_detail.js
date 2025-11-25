// Timesheet Detail JavaScript
function validateSubmission(event) {
    var totalHours = parseFloat(document.getElementById('gridForm').dataset.totalHours || '0');
    if (totalHours <= 0) {
        event.preventDefault();
        var modal = new bootstrap.Modal(document.getElementById('emptyTimesheetModal'));
        modal.show();
        return false;
    }
    return true;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    var gridForm = document.getElementById('gridForm');
    if (!gridForm) return;

    var inputs = gridForm.querySelectorAll('input[type="number"]');

    // Try to get CSRF token from input first, then cookie
    var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    var csrftoken = csrfInput ? csrfInput.value : getCookie('csrftoken');

    var numDays = parseInt(gridForm.dataset.numDays) || 7;

    // Debounce map to avoid spamming requests while digitando
    var saveTimers = new Map();

    inputs.forEach(function (input) {
        input.addEventListener('input', function () {
            calculateTotals();
            scheduleAutoSave(this);
            // Remove validation classes while typing
            this.classList.remove('is-valid', 'is-invalid');
        });
        input.addEventListener('blur', function () {
            autoSaveField(this);
        });
    });

    function calculateTotals() {
        var tbody = gridForm.querySelector('tbody');
        var rows = tbody.querySelectorAll('tr');

        rows.forEach(function (row) {
            var rowInputs = row.querySelectorAll('input[type="number"]');
            var rowTotal = 0;

            rowInputs.forEach(function (input) {
                var value = parseFloat(input.value) || 0;
                rowTotal += value;
            });

            var totalCell = row.querySelector('td.fw-bold');
            if (totalCell) {
                totalCell.textContent = rowTotal.toFixed(1);
            }
        });

        var dailyTotals = new Array(numDays).fill(0);

        rows.forEach(function (row) {
            var rowInputs = row.querySelectorAll('input[type="number"]');
            rowInputs.forEach(function (input, index) {
                var value = parseFloat(input.value) || 0;
                dailyTotals[index] += value;
            });
        });

        var footerCells = gridForm.querySelectorAll('tfoot td.text-center');
        dailyTotals.forEach(function (total, index) {
            if (footerCells[index]) {
                footerCells[index].textContent = total.toFixed(1);
            }
        });

        // Calculate grand total from row totals
        var rowTotals = [];
        rows.forEach(function (row) {
            var rowTotal = 0;
            var rowInputs = row.querySelectorAll('input[type="number"]');
            rowInputs.forEach(function (input) {
                rowTotal += parseFloat(input.value) || 0;
            });
            rowTotals.push(rowTotal);
        });

        var actualGrandTotal = rowTotals.reduce(function (sum, val) { return sum + val; }, 0);
        var grandTotalCell = document.getElementById('grandTotal');
        if (grandTotalCell) {
            grandTotalCell.textContent = actualGrandTotal.toFixed(1);
        }

        gridForm.dataset.totalHours = actualGrandTotal.toFixed(1);
    }

    function scheduleAutoSave(input) {
        if (saveTimers.has(input)) {
            clearTimeout(saveTimers.get(input));
        }
        var timer = setTimeout(function () {
            autoSaveField(input);
            saveTimers.delete(input);
        }, 500);
        saveTimers.set(input, timer);
    }

    function autoSaveField(input) {
        // Visual feedback: saving state (optional, maybe distinct border?)

        var formData = new FormData();
        formData.append('action', 'save_grid');
        formData.append('csrfmiddlewaretoken', csrftoken);
        // Enviar valor cru; string vazia significa excluir registro
        formData.append(input.name, input.value);

        var actionUrl = gridForm.getAttribute('action');
        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        }).then(function (response) {
            if (response.ok) {
                console.log('Auto-saved:', input.name, input.value);
                // Success feedback
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
                // Remove success class after 2 seconds
                setTimeout(function () {
                    input.classList.remove('is-valid');
                }, 2000);
            } else {
                console.error('Auto-save failed:', response.status);
                // Error feedback
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
            }
        }).catch(function (error) {
            console.error('Auto-save error:', error);
            // Error feedback
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        });
    }

    function saveAllFields() {
        var promises = [];
        var actionUrl = gridForm.getAttribute('action');
        inputs.forEach(function (input) {
            if (input.value && parseFloat(input.value) > 0) {
                var formData = new FormData();
                formData.append('action', 'save_grid');
                formData.append('csrfmiddlewaretoken', csrftoken);
                formData.append(input.name, input.value);

                var promise = fetch(actionUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrftoken
                    }
                });
                promises.push(promise);
            }
        });
        return Promise.all(promises);
    }

    // Attach to add row modal form
    var addRowForms = document.querySelectorAll('form[action*="timesheet_action"]');
    addRowForms.forEach(function (form) {
        var actionInput = form.querySelector('input[name="action"]');
        if (actionInput && actionInput.value === 'add_row') {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                console.log('Saving all fields before adding row...');
                saveAllFields().then(function () {
                    console.log('All fields saved, submitting form...');
                    form.submit();
                }).catch(function (error) {
                    console.error('Error saving fields:', error);
                    form.submit(); // Submit anyway
                });
            });
        }
    });

    calculateTotals();
});
