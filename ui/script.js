let isCapturing = false;

const startBtn = document.getElementById('startBtn');
const screenshotContainer = document.getElementById('screenshotContainer');

document.addEventListener('DOMContentLoaded', function () {
    console.log('Screen Capture Tool loaded');
});

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

function showError() {
    document.querySelector('.error').classList.remove('hidden')
}
function disableGemini() {
    document.querySelector('#geminiWarning').classList.remove('hidden')
    document.querySelector('#gemini').classList.add('perma-disabled')
}