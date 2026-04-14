// OOO Consolidator Frontend

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('oooForm');
    const submitBtn = document.getElementById('submitBtn');
    const clearBtn = document.getElementById('clearBtn');
    const resultMessage = document.getElementById('resultMessage');

    // Set default dates (tomorrow to 1 week from now)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(9, 0, 0, 0);

    const nextWeek = new Date(tomorrow);
    nextWeek.setDate(nextWeek.getDate() + 7);
    nextWeek.setHours(17, 0, 0, 0);

    document.getElementById('startDate').value = formatDateTimeLocal(tomorrow);
    document.getElementById('endDate').value = formatDateTimeLocal(nextWeek);

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await setOOO();
    });

    // Clear OOO button
    clearBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear your out-of-office status?')) {
            await clearOOO();
        }
    });

    // Format date for datetime-local input
    function formatDateTimeLocal(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    // Set OOO
    async function setOOO() {
        const formData = new FormData(form);

        // Build request payload
        const payload = {
            start_date: new Date(formData.get('start_date')).toISOString(),
            end_date: new Date(formData.get('end_date')).toISOString(),
            message: formData.get('message'),
            reason: formData.get('reason') || null,
            emergency_contact: formData.get('emergency_contact') || null,
            enable_slack: formData.get('enable_slack') === 'on',
            enable_calendar: formData.get('enable_calendar') === 'on',
            enable_email_signature: formData.get('enable_email_signature') === 'on',
            enable_email_autoreply: formData.get('enable_email_autoreply') === 'on'
        };

        // Validate dates
        if (new Date(payload.start_date) >= new Date(payload.end_date)) {
            showResult('error', 'End date must be after start date', {});
            return;
        }

        // Disable button and show loading
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.textContent = 'Setting OOO';

        try {
            const response = await fetch('/api/ooo/set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                showResult(result.success ? 'success' : 'error', result.message, result.details, result.errors);
            } else {
                showResult('error', 'Failed to set out-of-office', {}, { api: result.detail || 'Unknown error' });
            }
        } catch (error) {
            showResult('error', 'Network error', {}, { network: error.message });
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
            submitBtn.textContent = 'Set Out of Office';
        }
    }

    // Clear OOO
    async function clearOOO() {
        clearBtn.disabled = true;
        clearBtn.textContent = 'Clearing...';

        try {
            const response = await fetch('/api/ooo/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (response.ok) {
                showResult(result.success ? 'success' : 'error', result.message, result.details, result.errors);
            } else {
                showResult('error', 'Failed to clear out-of-office', {}, { api: result.detail || 'Unknown error' });
            }
        } catch (error) {
            showResult('error', 'Network error', {}, { network: error.message });
        } finally {
            clearBtn.disabled = false;
            clearBtn.textContent = 'Clear OOO (I\'m Back!)';
        }
    }

    // Show result message
    function showResult(type, message, details = {}, errors = {}) {
        resultMessage.className = `result-message show ${type}`;

        let html = `<h3>${type === 'success' ? '✅' : '❌'} ${message}</h3>`;

        // Show successful operations
        if (Object.keys(details).length > 0) {
            html += '<ul>';
            for (const [key, value] of Object.entries(details)) {
                if (value && value.success) {
                    html += `<li><strong>${formatKey(key)}:</strong> ${value.message || 'Updated'}</li>`;
                }
            }
            html += '</ul>';
        }

        // Show errors
        if (Object.keys(errors).length > 0) {
            html += '<h4>Errors:</h4><ul>';
            for (const [key, error] of Object.entries(errors)) {
                html += `<li><strong>${formatKey(key)}:</strong> ${error}</li>`;
            }
            html += '</ul>';
        }

        resultMessage.innerHTML = html;

        // Auto-hide after 10 seconds for success
        if (type === 'success') {
            setTimeout(() => {
                resultMessage.classList.remove('show');
            }, 10000);
        }
    }

    // Format key for display
    function formatKey(key) {
        return key
            .replace(/_/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Check configuration status on load
    checkStatus();

    async function checkStatus() {
        try {
            const response = await fetch('/api/ooo/status');
            const status = await response.json();

            // Could display configuration status to user
            console.log('Configuration status:', status);
        } catch (error) {
            console.error('Failed to check status:', error);
        }
    }
});
