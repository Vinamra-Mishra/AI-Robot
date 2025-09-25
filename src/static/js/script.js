
document.addEventListener('DOMContentLoaded', () => {
    const themeSwitch = document.getElementById('checkbox');
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    if (currentTheme === 'dark') {
        themeSwitch.checked = true;
    }

    themeSwitch.addEventListener('change', function(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => item.classList.remove('active'));
            tab.classList.add('active');

            const target = document.querySelector(`[data-tab="${tab.dataset.forTab}"]`);
            tabContents.forEach(content => content.classList.remove('active'));
            target.classList.add('active');
        });
    });

    // Robot Controls
    const sendCommand = (direction) => {
        fetch(`/move/${direction}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error));
    };

    document.getElementById('forward').addEventListener('click', () => sendCommand('forward'));
    document.getElementById('backward').addEventListener('click', () => sendCommand('backward'));
    document.getElementById('left').addEventListener('click', () => sendCommand('left'));
    document.getElementById('right').addEventListener('click', () => sendCommand('right'));
    document.getElementById('stop').addEventListener('click', () => sendCommand('stop'));
});
