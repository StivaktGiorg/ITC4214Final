// Script for Dark Mode Toggle
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

// Check if the user prefers dark mode (via localStorage or system settings)
if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-mode');
    darkModeToggle.innerText = 'Switch to Light Mode';
}

// Toggle dark mode when the button is clicked
darkModeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    const mode = body.classList.contains('dark-mode') ? 'Dark' : 'Light';
    darkModeToggle.innerText = `Switch to ${mode} Mode`;
    // Save the user preference to localStorage
    localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
});
