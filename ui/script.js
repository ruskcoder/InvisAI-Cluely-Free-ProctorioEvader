let isCapturing = false;

const startBtn = document.getElementById('startBtn');
const screenshotContainer = document.getElementById('screenshotContainer');

// AI Response tracking for voting summary
let aiResponses = {};
let completedAIs = [];

// Window dragging functionality
let isDragging = false;
let startX = 0;
let startY = 0;
let lastMoveTime = 0;
const DRAG_THROTTLE_MS = 16; // ~60fps

document.addEventListener('DOMContentLoaded', function () {
    console.log('Screen Capture Tool loaded');
    initializeTitleBarDrag();
    
    // Initialize screenshot container as hidden
    screenshotContainer.classList.add('hidden');
    
    // Load settings immediately to apply AI visibility and other settings
    loadSettingsOnStartup();
});

function initializeTitleBarDrag() {
    const titleBar = document.getElementById('titleBar');
    
    titleBar.addEventListener('mousedown', function(e) {
        // Only start dragging if clicking on the title bar itself, not on buttons
        if (e.target.closest('.title-bar-button')) {
            return;
        }
        
        isDragging = true;
        // Use screen coordinates consistently for better cross-resolution behavior
        startX = e.screenX;
        startY = e.screenY;
        
        console.log('Drag start - Screen:', startX, startY);
        
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
    
    // Throttle drag moves to improve performance
    const now = Date.now();
    if (now - lastMoveTime < DRAG_THROTTLE_MS) {
        return;
    }
    lastMoveTime = now;
    
    // Send current screen coordinates directly instead of calculating deltas
    const currentX = e.screenX;
    const currentY = e.screenY;
    
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.dragWindow(currentX, currentY).catch(err => {
            console.warn('Drag move failed:', err);
        });
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

// Function called by backend when window state changes
function updatePreviewState(isHidden) {
    isPreviewOff = isHidden;
    console.log("Window preview state updated:", isPreviewOff ? "hidden" : "visible");
}

// Preview functionality
let isPreviewOff = false;
function togglePreview() {
    if (window.pywebview && window.pywebview.api && !isPreviewOff) {
        pywebview.api.set_window_transparent()
            .then(response => {
                if (response.success) {
                    isPreviewOff = true;
                    console.log("Window hidden. Press any key or click mouse to restore.");
                } else {
                    console.error("Failed to hide window:", response.message);
                }
            })
            .catch(err => {
                console.error("Error hiding window:", err);
            });
    }
}

function restoreWindow() {
    if (window.pywebview && window.pywebview.api && isPreviewOff) {
        pywebview.api.restore_window()
            .then(response => {
                if (response.success) {
                    isPreviewOff = false;
                    console.log("Window restored.");
                } else {
                    console.error("Failed to restore window:", response.message);
                }
            })
            .catch(err => {
                console.error("Error restoring window:", err);
            });
    }
}

async function startCapture() {
    try {
        isCapturing = true;
        startBtn.disabled = true;
        startBtn.textContent = 'Capturing...';
        
        // Hide voting summary with animation
        hideVotingSummary();
        
        menus = document.querySelectorAll('.menu')
        menus.forEach(item =>
            item.classList.add('disabled')
        )
        // Clear any existing screenshot
        screenshotContainer.innerHTML = '';
        screenshotContainer.classList.add('hidden');

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
    const wrapper = document.createElement('div');
    wrapper.className = 'screenshot-wrapper';
    
    const img = document.createElement('img');
    img.src = imageData;
    img.alt = 'Captured Screenshot';
    
    const overlay = document.createElement('div');
    overlay.className = 'screenshot-overlay';
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-screenshot-btn';
    deleteBtn.onclick = deleteScreenshot;
    deleteBtn.innerHTML = '<span class="material-symbols-rounded">close</span>';
    
    overlay.appendChild(deleteBtn);
    wrapper.appendChild(img);
    wrapper.appendChild(overlay);

    screenshotContainer.innerHTML = '';
    screenshotContainer.appendChild(wrapper);
    screenshotContainer.classList.remove('hidden');

    resetButton();
}

function deleteScreenshot() {
    const screenshotContainer = document.getElementById('screenshotContainer');
    screenshotContainer.classList.add('hidden');
    
    // Clear the content after animation completes
    setTimeout(() => {
        screenshotContainer.innerHTML = '';
    }, 300); // Match transition duration
}

function hideVotingSummary() {
    const votingSummary = document.getElementById('votingSummary');
    votingSummary.classList.remove('show');
    setTimeout(() => {
        votingSummary.classList.add('hidden');
    }, 400); // Wait for animation to complete
}

function showVotingSummary() {
    const votingSummary = document.getElementById('votingSummary');
    votingSummary.classList.remove('hidden');
    // Use requestAnimationFrame to ensure the element is visible before adding show class
    requestAnimationFrame(() => {
        votingSummary.classList.add('show');
    });
}

function captureComplete(imageData) {
    displayScreenshot(imageData);
    
    // Reset AI tracking
    aiResponses = {};
    completedAIs = [];
    hideVotingSummary();
    
    menus = document.querySelectorAll('.menu')
    menus.forEach(item => {
        item.classList.remove('disabled')
        item.classList.add('working')
        item.classList.remove('ai-error')
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
            cancelCapture();
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
        menu.classList.remove('ai-error');
        const contentElem = menu.querySelector('.content-container .content');
        contentElem.innerHTML = content;

        const lines = content.split('<br>');
        let firstLineComplete = false;
        
        if (lines[0].trim() !== "") {
            lines[0] = `<b>${lines[0]}</b>`;
            contentElem.innerHTML = lines.join('<br>');
            
            // Update span and voting as soon as first line is available
            const spanElem = menu.querySelector('.title span');
            try {
                if (content.split('<br>').length > 1) {
                    const firstLineRaw = content.split('<br>')[0];
                    const firstLine = firstLineRaw.replace(/<[^>]*>/g, '');
                    const parts = firstLine.split(': ');
                    if (parts.length > 1) {
                        spanElem.textContent = parts[1];

                        // Parse the option and store it
                        const parsedOption = parseOptionFromResponse(parts[1]);
                        if (parsedOption) {
                            aiResponses[ai] = parsedOption;
                            // Only add to completedAIs if not already there
                            if (!completedAIs.includes(ai)) {
                                completedAIs.push(ai);
                                updateVotingSummary();
                            }
                            firstLineComplete = true;
                        }
                    }
                }
            } catch (error) {
                console.error('Error parsing AI response:', error);
            }
        }

        if (complete || firstLineComplete) {
            menu.classList.remove('working');
        } else {
            menu.classList.add('working');
        }
    }
}

function parseOptionFromResponse(responseText) {
    // Clean up the response text
    const cleanText = responseText.replace(/<[^>]*>/g, '').trim();
    
    // Look for patterns like "(A) Option text" or "(B) Some answer"
    let optionMatch = cleanText.match(/\(([A-Z])\)\s*(.+)/);
    
    // If that doesn't work, try to find option letter at the start
    if (!optionMatch) {
        optionMatch = cleanText.match(/^([A-Z])\)\s*(.+)/);
    }
    
    // Try another pattern: "A) Option text"
    if (!optionMatch) {
        optionMatch = cleanText.match(/^([A-Z])\)\s*(.+)/);
    }
    
    if (optionMatch) {
        return {
            letter: optionMatch[1],
            text: optionMatch[2].trim()
        };
    }
    
    // Last resort: look for single letter options
    const singleLetterMatch = cleanText.match(/\b([A-Z])\b/);
    if (singleLetterMatch && ['A', 'B', 'C', 'D', 'E'].includes(singleLetterMatch[1])) {
        return {
            letter: singleLetterMatch[1],
            text: cleanText
        };
    }
    
    return null;
}

function updateVotingSummary() {
    if (completedAIs.length < 1) {
        return; // Don't show summary until at least 1 AI is done
    }
    
    // Count votes for each option
    const votes = {};
    completedAIs.forEach(ai => {
        const response = aiResponses[ai];
        if (response) {
            const key = response.letter;
            if (!votes[key]) {
                votes[key] = {
                    count: 0,
                    text: response.text,
                    letter: response.letter
                };
            }
            votes[key].count++;
        }
    });
    
    // Sort options by vote count (descending)
    const sortedOptions = Object.values(votes).sort((a, b) => b.count - a.count);
    
    // Generate summary HTML
    const summaryContent = document.getElementById('summaryContent');
    summaryContent.innerHTML = '';
    
    sortedOptions.forEach((option, index) => {
        const item = document.createElement('div');
        item.className = 'summary-item';
        
        const totalAIs = completedAIs.length;
        let statusIcon, statusClass;
        
        if (option.count === totalAIs) {
            statusIcon = '✅';
            statusClass = 'consensus';
        } else if (option.count >= Math.ceil(totalAIs / 2)) {
            statusIcon = '✅';
            statusClass = 'majority';
        } else {
            statusIcon = '⚠';
            statusClass = 'minority';
        }
        
        const optionTextClass = index === 0 ? 'option-text pulse' : 'option-text';
        
        item.innerHTML = `
            <span class="status-icon ${statusClass}">${statusIcon}</span>
            <span class="${optionTextClass}">(${option.letter}) ${option.text}</span>
            <span class="vote-count">(${option.count}/${totalAIs})</span>
        `;
        
        summaryContent.appendChild(item);
        
        // Remove pulse class after animation completes (only for top option)
        if (index === 0) {
            setTimeout(() => {
                const textElement = item.querySelector('.option-text');
                if (textElement) {
                    textElement.classList.remove('pulse');
                }
            }, 600); // Match animation duration
        }
    });
    
    // Show the voting summary with animation
    showVotingSummary();
}

function showError() {
    document.querySelector('.error').classList.remove('hidden')
}
function disableGemini() {
    document.querySelector('#geminiWarning').classList.remove('hidden')
    document.querySelector('#gemini').classList.add('perma-disabled')
}
function disableCopilot() {
    document.querySelector('#copilotWarning').classList.remove('hidden')
    document.querySelector('#copilot').classList.add('perma-disabled')
}
function warningTesseract() {
    document.querySelector('#tesseractWarning').classList.remove('hidden')
    document.querySelector('#gemini').classList.add('perma-disabled')
    document.querySelector('#qwen').classList.add('perma-disabled')
    document.querySelector('#deepseek').classList.add('perma-disabled')
}
function aiError(ai, errorMessage = 'An error occurred.') {
    const menu = document.querySelector('#' + ai);
    menu.classList.add('ai-error');
    
    // Display the error message in the content area
    const contentElem = menu.querySelector('.content-container .content');
    contentElem.innerHTML = `<span style="color: #ff6b6b; font-style: italic;">Error: ${errorMessage}</span>`;
    
    // Update the title span to show error status
    const spanElem = menu.querySelector('.title span');
    spanElem.textContent = 'Error';
    
    // Don't count errored AIs in the voting summary
}

// Settings functions
function toggleSettings() {
    const settingsPage = document.getElementById('settingsPage');
    
    if (settingsPage.classList.contains('show')) {
        closeSettings();
    } else {
        openSettings();
    }
}

function openSettings() {
    const settingsPage = document.getElementById('settingsPage');
    const mainContent = document.getElementById('mainContent');
    
    settingsPage.classList.remove('hidden');
    setTimeout(() => {
        settingsPage.classList.add('show');
    }, 10);
    
    // Update title bar for settings mode
    updateTitleBarForSettings(true);
    
    // Load current settings
    loadSettings();
}

function closeSettings() {
    const settingsPage = document.getElementById('settingsPage');
    
    settingsPage.classList.remove('show');
    setTimeout(() => {
        settingsPage.classList.add('hidden');
    }, 300);
    
    // Restore title bar to normal mode
    updateTitleBarForSettings(false);
}

function updateTitleBarForSettings(isSettingsMode) {
    const appIcon = document.getElementById('appIcon');
    const appTitle = document.getElementById('appTitle');
    const settingsBtnIcon = document.getElementById('settingsBtnIcon');
    
    if (isSettingsMode) {
        // Change to back arrow and "Settings" title
        appIcon.textContent = 'arrow_back';
        appIcon.classList.add('back-arrow');
        appTitle.textContent = 'Settings';
        settingsBtnIcon.textContent = 'settings'; // Keep settings icon, don't change to back arrow
        
        // Make the icon clickable to go back
        appIcon.onclick = closeSettings;
    } else {
        // Restore to normal
        appIcon.textContent = 'visibility';
        appIcon.classList.remove('back-arrow');
        appTitle.textContent = 'InvisAI';
        settingsBtnIcon.textContent = 'settings';
        
        // Remove click handler
        appIcon.onclick = null;
    }
}

function loadSettingsOnStartup() {
    // Wait a bit for pywebview API to be ready
    setTimeout(() => {
        if (window.pywebview && window.pywebview.api) {
            pywebview.api.getSettings().then(settings => {
                console.log('Applying settings on startup:', settings);
                
                // Apply AI visibility based on settings
                const aiSettings = [
                    { key: 'enableChatGPT', elementId: 'chatgpt' },
                    { key: 'enableCopilot', elementId: 'copilot' },
                    { key: 'enableGemini', elementId: 'gemini' },
                    { key: 'enableQwen', elementId: 'qwen' },
                    { key: 'enableDeepseek', elementId: 'deepseek' }
                ];
                
                aiSettings.forEach(ai => {
                    const isEnabled = settings[ai.key] !== false; // Default to true
                    
                    // Hide/show AI element based on setting
                    const aiElement = document.getElementById(ai.elementId);
                    if (aiElement) {
                        if (isEnabled) {
                            aiElement.classList.remove('hidden');
                        } else {
                            aiElement.classList.add('hidden');
                        }
                    }
                });
            }).catch(err => {
                console.error('Error loading settings on startup:', err);
                // Retry after a longer delay if API not ready
                setTimeout(() => loadSettingsOnStartup(), 500);
            });
        } else {
            // Retry if pywebview API not ready yet
            setTimeout(() => loadSettingsOnStartup(), 200);
        }
    }, 100);
}

function loadSettings() {
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.getSettings().then(settings => {
            const renameToggle = document.getElementById('renameWindowToggle');
            const isRenameEnabled = settings.renameWindow || false;
            renameToggle.checked = isRenameEnabled;
            
            // Always hide restart warning on settings load (it should only show when user changes the setting)
            const restartWarning = document.getElementById('restartWarning');
            restartWarning.classList.add('hidden');
            
            // Load AI settings and update UI visibility
            const aiSettings = [
                { key: 'enableChatGPT', toggleId: 'enableChatGPTToggle', elementId: 'chatgpt' },
                { key: 'enableCopilot', toggleId: 'enableCopilotToggle', elementId: 'copilot' },
                { key: 'enableGemini', toggleId: 'enableGeminiToggle', elementId: 'gemini' },
                { key: 'enableQwen', toggleId: 'enableQwenToggle', elementId: 'qwen' },
                { key: 'enableDeepseek', toggleId: 'enableDeepseekToggle', elementId: 'deepseek' }
            ];
            
            aiSettings.forEach(ai => {
                const toggle = document.getElementById(ai.toggleId);
                const isEnabled = settings[ai.key] !== false; // Default to true
                toggle.checked = isEnabled;
                
                // Hide/show AI element based on setting
                const aiElement = document.getElementById(ai.elementId);
                if (aiElement) {
                    if (isEnabled) {
                        aiElement.classList.remove('hidden');
                    } else {
                        aiElement.classList.add('hidden');
                    }
                }
            });
            
            // Load hotkey settings
            const sHotkeyToggle = document.getElementById('enableSHotkeyToggle');
            const isSHotkeyEnabled = settings.enableSHotkey === true; // Default to false
            sHotkeyToggle.checked = isSHotkeyEnabled;
        }).catch(err => {
            console.error('Error loading settings:', err);
        });
    }
}

function updateRenameSetting(enabled) {
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.updateSetting('renameWindow', enabled).then(() => {
            console.log('Rename window setting updated:', enabled);
            
            // Always show restart warning when setting is changed
            const restartWarning = document.getElementById('restartWarning');
            restartWarning.classList.remove('hidden');
        }).catch(err => {
            console.error('Error updating setting:', err);
        });
    }
}

function updateAISetting(settingKey, enabled) {
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.updateSetting(settingKey, enabled).then(() => {
            console.log(`${settingKey} setting updated:`, enabled);
            
            // Immediately update UI visibility based on the setting
            const aiElementMap = {
                'enableChatGPT': 'chatgpt',
                'enableCopilot': 'copilot',
                'enableGemini': 'gemini',
                'enableQwen': 'qwen',
                'enableDeepseek': 'deepseek'
            };
            
            const elementId = aiElementMap[settingKey];
            if (elementId) {
                const aiElement = document.getElementById(elementId);
                if (aiElement) {
                    if (enabled) {
                        aiElement.classList.remove('hidden');
                    } else {
                        aiElement.classList.add('hidden');
                    }
                }
            }
        }).catch(err => {
            console.error('Error updating AI setting:', err);
        });
    }
}

function updateHotkeySettings(settingKey, enabled) {
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.updateSetting(settingKey, enabled).then(() => {
            console.log(`${settingKey} setting updated:`, enabled);
        }).catch(err => {
            console.error('Error updating hotkey setting:', err);
        });
    }
}

async function cancelCapture() {
    try {
        console.log('Cancelling capture...');
        const result = await pywebview.api.cancelCapture();
        
        if (result.success) {
            console.log('Capture cancelled successfully');
        } else {
            console.error('Cancel failed:', result.message);
        }
        
        resetButton();
    } catch (error) {
        console.error('Error cancelling capture:', error);
        resetButton();
    }
}

function restartApp() {
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.restartApp().then(() => {
            console.log('App restart initiated');
        }).catch(err => {
            console.error('Error restarting app:', err);
        });
    }
}

function hideRestartWarning() {
    const restartWarning = document.getElementById('restartWarning');
    restartWarning.classList.add('hidden');
}

function runHarGrabber() {
    console.log('Starting HAR capture...');
    
    // Hide the copilot warning and show the HAR instructions
    const copilotWarning = document.getElementById('copilotWarning');
    const harInstructions = document.getElementById('harInstructions');
    
    copilotWarning.classList.add('hidden');
    harInstructions.classList.remove('hidden');
    
    // Start the HAR capture process
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.startHarCapture().then(result => {
            if (result.success) {
                console.log('HAR capture started successfully');
            } else {
                console.error('Failed to start HAR capture:', result.message);
                // Show error and revert UI
                alert('Failed to start HAR capture: ' + result.message);
                harInstructions.classList.add('hidden');
                copilotWarning.classList.remove('hidden');
            }
        }).catch(error => {
            console.error('Error starting HAR capture:', error);
            alert('Error starting HAR capture: ' + error);
            harInstructions.classList.add('hidden');
            copilotWarning.classList.remove('hidden');
        });
    }
}

function completeHarCapture() {
    console.log('Completing HAR capture...');
    
    // Disable the button to prevent multiple clicks
    const completeBtn = document.getElementById('completeHarBtn');
    const originalText = completeBtn.innerHTML;
    completeBtn.disabled = true;
    completeBtn.innerHTML = '<span class="material-symbols-rounded">hourglass_empty</span> Completing...';
    
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.completeHarCapture().then(result => {
            if (result.success) {
                console.log('HAR capture completed successfully');
                
                // Hide the HAR instructions
                const harInstructions = document.getElementById('harInstructions');
                harInstructions.classList.add('hidden'); 
                
                // Check if Copilot is now available
                pywebview.api.recheckAIAvailability().then(recheckResult => {
                    if (recheckResult.success && recheckResult.copilot_enabled) {
                        console.log('Copilot is now available, enabling in UI');
                        enableCopilot();
                    } else {
                        console.log('Copilot is still not available');
                        // Show the copilot warning again
                        const copilotWarning = document.getElementById('copilotWarning');
                        copilotWarning.classList.remove('hidden');
                    }
                }).catch(recheckError => {
                    console.error('Error rechecking AI availability:', recheckError);
                    // Show the copilot warning again as fallback
                    const copilotWarning = document.getElementById('copilotWarning');
                    copilotWarning.classList.remove('hidden');
                });
            } else {
                console.error('Failed to complete HAR capture:', result.message);
                alert('Failed to complete HAR capture: ' + result.message);
                
                // Re-enable the button
                completeBtn.disabled = false;
                completeBtn.innerHTML = originalText;
            }
        }).catch(error => {
            console.error('Error completing HAR capture:', error);
            alert('Error completing HAR capture: ' + error);
            
            // Re-enable the button
            completeBtn.disabled = false;
            completeBtn.innerHTML = originalText;
        });
    }
}

function onHarCaptureBrowserClosed() {
    console.log('HAR capture browser was closed unexpectedly');
    
    // Hide the HAR instructions
    const harInstructions = document.getElementById('harInstructions');
    harInstructions.classList.add('hidden');
    
    // Show the copilot warning again
    const copilotWarning = document.getElementById('copilotWarning');
    copilotWarning.classList.remove('hidden');
    
    // Show a message to the user
}

function enableCopilot() {
    document.querySelector('#copilotWarning').classList.add('hidden')
    document.querySelector('#copilot').classList.remove('perma-disabled')
    console.log('Copilot enabled in UI')
}