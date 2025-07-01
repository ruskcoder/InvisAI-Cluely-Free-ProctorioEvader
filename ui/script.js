let isCapturing = false;

const startBtn = document.getElementById('startBtn');
const screenshotContainer = document.getElementById('screenshotContainer');

// Window dragging functionality
let isDragging = false;
let startX = 0;
let startY = 0;

document.addEventListener('DOMContentLoaded', function () {
    console.log('Screen Capture Tool loaded');
    initializeTitleBarDrag();
});

function initializeTitleBarDrag() {
    const titleBar = document.getElementById('titleBar');
    
    titleBar.addEventListener('mousedown', function(e) {
        // Only start dragging if clicking on the title bar itself, not on buttons
        if (e.target.closest('.title-bar-button')) {
            return;
        }
        
        isDragging = true;
        startX = e.screenX;
        startY = e.screenY;
        
        // Get the current window position when drag starts
        if (window.pywebview && window.pywebview.api) {
            pywebview.api.startWindowDrag(startX, startY);
        }
        
        document.addEventListener('mousemove', handleDragMove);
        document.addEventListener('mouseup', handleDragEnd);
        
        e.preventDefault();
    });
}

function handleDragMove(e) {
    if (!isDragging) return;
    
    const currentX = e.screenX;
    const currentY = e.screenY;
    
    // Calculate the difference from start position
    const deltaX = currentX - startX;
    const deltaY = currentY - startY;
    
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.dragWindow(deltaX, deltaY);
    }
}

function handleDragEnd() {
    if (isDragging) {
        isDragging = false;
        document.removeEventListener('mousemove', handleDragMove);
        document.removeEventListener('mouseup', handleDragEnd);
        
        if (window.pywebview && window.pywebview.api) {
            pywebview.api.endWindowDrag();
        }
    }
}

// Window control functions
function closeWindow() {
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.closeWindow();
    }
}

async function startCapture() {
    try {
        isCapturing = true;
        startBtn.disabled = true;
        startBtn.textContent = 'Capturing...';
        menus = document.querySelectorAll('.menu')
        menus.forEach(item =>
            item.classList.add('disabled')
        )
        // Clear any existing screenshot
        screenshotContainer.innerHTML = '';

        const result = await pywebview.api.startCapture();

        if (result.success) {
            console.log('Capture started successfully');
        } else {
            console.error('Capture failed:', result.message);
            resetButton();
        }
    } catch (error) {
        console.error('Error starting capture:', error);
        resetButton();
    }
}

function resetButton() {
    isCapturing = false;
    startBtn.disabled = false;
    startBtn.textContent = 'Start Capture';
}

function displayScreenshot(imageData) {
    const img = document.createElement('img');
    img.src = imageData;
    img.alt = 'Captured Screenshot';

    screenshotContainer.innerHTML = '';
    screenshotContainer.appendChild(img);

    resetButton();
}

function captureComplete(imageData) {
    displayScreenshot(imageData);
    menus = document.querySelectorAll('.menu')
    menus.forEach(item => {
        item.classList.remove('disabled')
        item.classList.add('working')
        const contentContainer = item.querySelector('.content-container');
        const contentElem = contentContainer.querySelector('.content');
        contentElem.textContent = ""
    }
    )
}

function captureError(error) {
    console.error('Capture failed:', error);
    resetButton();
}

document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        if (isCapturing) {
            resetButton();
        }
    }
});

const menuItems = document.querySelectorAll('.menu .title');
menuItems.forEach(item => {
    item.addEventListener('click', function () {
        if (item.parentElement.classList.contains('open')) {
            item.parentElement.classList.remove('open');
        } else {
            item.parentElement.classList.add('open');
        }
    });
});

function updateAI(ai, content, complete) {
    if (isCapturing == false) {
        const menu = document.getElementById(ai);
        menu.classList.remove('disabled');
        const contentElem = menu.querySelector('.content-container .content');
        contentElem.innerHTML = content;

        const lines = content.split('<br>');
        if (lines[0].trim() !== "") {
            lines[0] = `<b>${lines[0]}</b>`;
            contentElem.innerHTML = lines.join('<br>');
        }

        if (complete) {
            menu.classList.remove('working');
            const spanElem = menu.querySelector('.title span');
            try {
                const firstLineRaw = content.split('<br>')[0];
                const firstLine = firstLineRaw.replace(/<[^>]*>/g, '');
                const parts = firstLine.split(': ');
                if (parts.length > 1) {
                    spanElem.textContent = parts[1];
                }
            } catch (error) {
                console.error('Error parsing AI response:', error);
            }
        } else {
            menu.classList.add('working');
        }
    }
}

function showError() {
    document.querySelector('.error').classList.remove('hidden')
}
function disableGemini() {
    document.querySelector('#geminiWarning').classList.remove('hidden')
    document.querySelector('#gemini').classList.add('perma-disabled')
}
function warningTesseract() {
    document.querySelector('#tesseractWarning').classList.remove('hidden')
    document.querySelector('#gemini').classList.add('perma-disabled')
    document.querySelector('#qwen').classList.add('perma-disabled')
    document.querySelector('#deepseek').classList.add('perma-disabled')
}