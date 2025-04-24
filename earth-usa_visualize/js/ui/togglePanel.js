export function addToggleFunctionality(panel, onToggleCallback) {
    const toggleBtn = document.createElement('button');
    toggleBtn.classList.add('toggle-panel-btn');
    toggleBtn.textContent = '❮';
    document.body.appendChild(toggleBtn);

    toggleBtn.addEventListener('click', () => {
        panel.classList.toggle('hidden');
        toggleBtn.textContent = panel.classList.contains('hidden') ? '❯' : '❮';

        if (onToggleCallback) {
            onToggleCallback();
        }
    });

    const updateButtonPosition = () => {
        const panelRect = panel.getBoundingClientRect();
        toggleBtn.style.top = `${panelRect.top + panelRect.height / 2}px`;
    };

    updateButtonPosition();

    window.addEventListener('resize', updateButtonPosition);
}
