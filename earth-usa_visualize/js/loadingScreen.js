export function showLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'flex'; // Display the loading screen
    }
}

export function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        // Add a delay to ensure smooth animation completion
        setTimeout(() => {
            loadingScreen.style.opacity = '0'; // Fade-out animation
            setTimeout(() => {
                loadingScreen.style.display = 'none'; // Hide the loading screen
            }, 500); // Match the CSS animation duration
        }, 300); // Ensure the page is fully loaded before starting the fade-out
    }
}
