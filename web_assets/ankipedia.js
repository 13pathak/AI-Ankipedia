// Ankipedia JS - Injected into Anki Reviewer
// Based on content.js from Chrome Extension, adapted for Anki

var Ankipedia = (function () {
    let popup = null;
    let activeSelection = null;

    function init() {
        document.addEventListener('mouseup', onMouseUp);
        document.addEventListener('mousedown', onMouseDown);
        console.log("Ankipedia JS Initialized");
        // Debug Alert
        // alert("AI Ankipedia: JS Injected Successfully!"); 
    }

    function onMouseUp(event) {
        // slight delay to let selection finalize
        setTimeout(() => {
            const selection = window.getSelection();
            const text = selection.toString().trim();

            // console.log("Ankipedia Selection:", text);

            if (text.length > 0 && text.split(/\s+/).length <= 6) {
                const rect = selection.getRangeAt(0).getBoundingClientRect();
                activeSelection = { text: text, rect: rect };

                showPopup(rect.left, rect.bottom, text);

                if (window.pycmd) {
                    pycmd(`ankipedia_trigger:${text}`);
                } else {
                    console.log("pycmd not found (not in Anki?)");
                }
            }
        }, 100);
    }

    function onMouseDown(event) {
        // If clicking outside popup, close it
        if (popup && !popup.contains(event.target)) {
            removePopup();
        }
    }

    function showPopup(x, y, initialText) {
        removePopup(); // Close existing

        popup = document.createElement('div');
        popup.id = 'ankipedia-popup';
        popup.className = 'ankipedia-popup';
        popup.innerHTML = `
            <div class="ankipedia-header">
                <span class="ankipedia-title">Defining: "${initialText}"</span>
                <span class="ankipedia-close" onclick="Ankipedia.removePopup()">×</span>
            </div>
            <div class="ankipedia-content" id="ankipedia-content">
                <div class="ankipedia-loading">Loading definition...</div>
            </div>
        `;

        document.body.appendChild(popup);

        // Position
        const pRect = popup.getBoundingClientRect();
        let top = y + 10;
        let left = x;

        // Boundary checks
        if (left + pRect.width > window.innerWidth) {
            left = window.innerWidth - pRect.width - 20;
        }
        if (top + pRect.height > window.innerHeight) {
            top = y - pRect.height - 10; // flip to top
        }

        popup.style.top = `${top}px`;
        popup.style.left = `${left}px`;
    }

    function updatePopup(content, rawResult) {
        if (!popup) return;
        const container = document.getElementById('ankipedia-content');
        if (container) {
            // Basic markdown parsing
            let safeHtml = content.replace(/</g, "&lt;").replace(/>/g, "&gt;");

            // Fix: ### Header
            safeHtml = safeHtml.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            safeHtml = safeHtml.replace(/^## (.*$)/gim, '<h2>$1</h2>');
            safeHtml = safeHtml.replace(/^# (.*$)/gim, '<h1>$1</h1>');

            // Fix: **Bold**
            safeHtml = safeHtml.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

            // Fix: - List item
            safeHtml = safeHtml.replace(/^\- (.*$)/gim, '<li style="margin-left: 15px;">$1</li>');

            // Fix: Newlines
            safeHtml = safeHtml.replace(/\n/g, '<br>');

            container.innerHTML = safeHtml;

            // Add Interaction Buttons (Save, etc.)
            const actions = document.createElement('div');
            actions.className = 'ankipedia-actions';
            actions.innerHTML = `
                <button onclick="Ankipedia.saveDefinition()">Save to History</button>
            `;
            container.appendChild(actions);

            // Store result for saving
            popup.dataset.lastResult = JSON.stringify(rawResult);
        }
    }

    function saveDefinition() {
        if (!popup || !popup.dataset.lastResult) return;
        const result = JSON.parse(popup.dataset.lastResult);

        if (window.pycmd) {
            pycmd(`ankipedia_save:${JSON.stringify(result)}`);
        }

        // Show saved indicator
        const btn = popup.querySelector('button');
        if (btn) {
            btn.textContent = "Saved!";
            btn.disabled = true;
        }

        setTimeout(removePopup, 1500);
    }

    function removePopup() {
        if (popup) {
            popup.remove();
            popup = null;
        }
    }

    // Expose public methods
    return {
        init: init,
        removePopup: removePopup,
        updatePopup: updatePopup,
        saveDefinition: saveDefinition
    };

})();

// Start
Ankipedia.init();
