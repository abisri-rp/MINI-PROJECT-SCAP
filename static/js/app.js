/**
 * SCAP Interactive Client-Side JavaScript
 * Handles drag & drop uploads, assessment timers, synthesizer actions, and UI interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            if (sidebar.style.transform === 'translateX(0px)') {
                sidebar.style.transform = 'translateX(-100%)';
            } else {
                sidebar.style.transform = 'translateX(0px)';
            }
        });
    }

    // 2. Resume File Drag and Drop Zone
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resume-file-input');
    const fileNameDisplay = document.getElementById('selected-file-name');

    if (dropzone && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                updateFileDisplay(files[0].name);
            }
        });

        dropzone.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                updateFileDisplay(fileInput.files[0].name);
            }
        });

        function updateFileDisplay(name) {
            if (fileNameDisplay) {
                fileNameDisplay.textContent = `Selected: ${name}`;
                fileNameDisplay.style.display = 'block';
            }
        }
    }

    // 3. Timed Aptitude Assessment Countdown Clock
    const timerElement = document.getElementById('aptitude-timer');
    if (timerElement) {
        let totalSeconds = parseInt(timerElement.dataset.seconds || 900, 10); // default 15 minutes
        const timerInterval = setInterval(() => {
            if (totalSeconds <= 0) {
                clearInterval(timerInterval);
                alert("Time is up! Your aptitude assessment will be automatically submitted now.");
                const quizForm = document.getElementById('aptitude-form');
                if (quizForm) quizForm.submit();
                return;
            }
            totalSeconds--;
            const mins = Math.floor(totalSeconds / 60);
            const secs = totalSeconds % 60;
            timerElement.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
            
            // Visual warning when under 2 minutes
            if (totalSeconds < 120) {
                timerElement.style.color = '#ef4444';
                timerElement.style.fontWeight = '800';
            }
        }, 1000);
    }

    // 4. Quick Demo Login Credentials Auto-Fill
    window.fillCredentials = function(email, password) {
        const emailField = document.getElementById('login-email');
        const pwdField = document.getElementById('login-password');
        if (emailField && pwdField) {
            emailField.value = email;
            pwdField.value = password;
        }
    };
});
