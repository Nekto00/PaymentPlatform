// Базовый JavaScript
console.log('Static files are working!');

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 500);
        });
    }, 5000);
});
