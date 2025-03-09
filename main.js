document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const elements = {
        // Sliders and inputs
        hueMin: document.getElementById('hue-min'),
        hueMax: document.getElementById('hue-max'),
        satMin: document.getElementById('sat-min'),
        satMax: document.getElementById('sat-max'),
        valMin: document.getElementById('val-min'),
        valMax: document.getElementById('val-max'),
        sizeMin: document.getElementById('size-min'),
        sizeMax: document.getElementById('size-max'),
        circularity: document.getElementById('circularity'),
        overlapSensitivity: document.getElementById('overlap-sensitivity'),
        erosion: document.getElementById('erosion'),
        dilation: document.getElementById('dilation'),
        
        // Display values
        hueMinValue: document.getElementById('hue-min-value'),
        hueMaxValue: document.getElementById('hue-max-value'),
        satMinValue: document.getElementById('sat-min-value'),
        satMaxValue: document.getElementById('sat-max-value'),
        valMinValue: document.getElementById('val-min-value'),
        valMaxValue: document.getElementById('val-max-value'),
        sizeMinValue: document.getElementById('size-min-value'),
        sizeMaxValue: document.getElementById('size-max-value'),
        circularityValue: document.getElementById('circularity-value'),
        overlapSensitivityValue: document.getElementById('overlap-sensitivity-value'),
        erosionValue: document.getElementById('erosion-value'),
        dilationValue: document.getElementById('dilation-value'),
        
        // Region inputs
        regionX: document.getElementById('region-x'),
        regionY: document.getElementById('region-y'),
        regionWidth: document.getElementById('region-width'),
        regionHeight: document.getElementById('region-height'),
        
        // Buttons
        selectRegion: document.getElementById('select-region'),
        previewDetection: document.getElementById('preview-detection'),
        startClicking: document.getElementById('start-clicking'),
        stopClicking: document.getElementById('stop-clicking'),
        
        // Output elements
        previewImage: document.getElementById('preview-image'),
        previewPlaceholder: document.getElementById('preview-placeholder'),
        previewLoading: document.getElementById('preview-loading'),
        cellsDetected: document.getElementById('cells-detected'),
        cellsClicked: document.getElementById('cells-clicked'),
        successRate: document.getElementById('success-rate'),
        logs: document.getElementById('logs')
    };
    
    // Default HSV values for different colors
    const defaultHSVRanges = {
        green: {
            hue: [40, 80],
            saturation: [50, 255],
            value: [50, 255]
        },
        red: {
            hue: [0, 10, 160, 179], // Red wraps around in HSV, so two ranges are needed
            saturation: [50, 255],
            value: [50, 255]
        }
    };
    
    // Current state
    let state = {
        cellColor: 'green',
        isClicking: false,
        cellsDetected: 0,
        cellsClicked: 0
    };
    
    // Initialize UI values
    updateSliderValues();
    
    // Set up event listeners for sliders
    setupSliderListeners();
    
    // Set up color radio button change listener
    setupColorChangeListener();
    
    // Set up button click handlers
    elements.selectRegion.addEventListener('click', handleSelectRegion);
    elements.previewDetection.addEventListener('click', handlePreviewDetection);
    elements.startClicking.addEventListener('click', handleStartClicking);
    elements.stopClicking.addEventListener('click', handleStopClicking);
    
    // Function to update all slider value displays
    function updateSliderValues() {
        elements.hueMinValue.textContent = elements.hueMin.value;
        elements.hueMaxValue.textContent = elements.hueMax.value;
        elements.satMinValue.textContent = elements.satMin.value;
        elements.satMaxValue.textContent = elements.satMax.value;
        elements.valMinValue.textContent = elements.valMin.value;
        elements.valMaxValue.textContent = elements.valMax.value;
        elements.sizeMinValue.textContent = elements.sizeMin.value;
        elements.sizeMaxValue.textContent = elements.sizeMax.value;
        elements.circularityValue.textContent = (elements.circularity.value / 100).toFixed(1);
        elements.overlapSensitivityValue.textContent = (elements.overlapSensitivity.value / 100).toFixed(1);
        elements.erosionValue.textContent = elements.erosion.value;
        elements.dilationValue.textContent = elements.dilation.value;
    }
    
    // Set up event listeners for all sliders
    function setupSliderListeners() {
        const sliders = [
            elements.hueMin, elements.hueMax, 
            elements.satMin, elements.satMax,
            elements.valMin, elements.valMax,
            elements.sizeMin, elements.sizeMax,
            elements.circularity, elements.overlapSensitivity,
            elements.erosion, elements.dilation
        ];
        
        sliders.forEach(slider => {
            slider.addEventListener('input', updateSliderValues);
        });
    }
    
    // Handle color radio button changes
    function setupColorChangeListener() {
        const radioButtons = document.querySelectorAll('input[name="cell-color"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                state.cellColor = this.value;
                updateHSVRangesForColor(this.value);
                addLog(`Changed target color to ${this.value}`);
            });
        });
    }
    
    // Update HSV ranges based on selected color
    function updateHSVRangesForColor(color) {
        const ranges = defaultHSVRanges[color];
        
        if (color === 'red') {
            // For red, which wraps around in HSV space, set to lower range
            elements.hueMin.value = ranges.hue[0];
            elements.hueMax.value = ranges.hue[1];
            addLog("Note: Red color may require adjusting hue range (try 0-10 or 160-179)", "info");
        } else {
            elements.hueMin.value = ranges.hue[0];
            elements.hueMax.value = ranges.hue[1];
        }
        
        elements.satMin.value = ranges.saturation[0];
        elements.satMax.value = ranges.saturation[1];
        elements.valMin.value = ranges.value[0];
        elements.valMax.value = ranges.value[1];
        
        updateSliderValues();
    }
    
    // Handle select region button click
    function handleSelectRegion() {
        addLog("Select region functionality would open a screen selection UI", "info");
        addLog("For this demo, please set region values manually", "info");
        // This would normally integrate with a screen region selector
    }
    
    // Handle preview detection button click
    function handlePreviewDetection() {
        const params = getDetectionParams();
        showLoading(true);
        
        // Simulate API call to Python backend
        setTimeout(() => {
            // This would normally be an actual fetch to the backend
            fetch('/api/preview-detection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            })
            .then(response => {
                // In the real implementation, this would handle the actual response
                // For demo purposes, we'll simulate a successful response
                simulateDetectionResponse();
            })
            .catch(error => {
                addLog(`Error during detection preview: ${error.message}`, "error");
                showLoading(false);
            });
        }, 1500);
    }
    
    // Handle start clicking button click
    function handleStartClicking() {
        const params = getDetectionParams();
        
        // Update UI state
        elements.startClicking.disabled = true;
        elements.stopClicking.disabled = false;
        elements.previewDetection.disabled = true;
        state.isClicking = true;
        
        addLog("Starting cell clicking process...", "info");
        
        // Simulate API call to Python backend
        setTimeout(() => {
            // This would be a real fetch to the Python backend in the actual implementation
            simulateClickingProcess(params);
        }, 1000);
    }
    
    // Handle stop clicking button click
    function handleStopClicking() {
        // Update UI state
        elements.startClicking.disabled = false;
        elements.stopClicking.disabled = true;
        elements.previewDetection.disabled = false;
        state.isClicking = false;
        
        addLog("Stopped cell clicking process.", "info");
        
        // In the real implementation, this would send a stop signal to the Python backend
    }
    
    // Get all detection parameters from the UI
    function getDetectionParams() {
        return {
            cellColor: state.cellColor,
            hsvRange: {
                hueMin: parseInt(elements.hueMin.value),
                hueMax: parseInt(elements.hueMax.value),
                satMin: parseInt(elements.satMin.value),
                satMax: parseInt(elements.satMax.value),
                valMin: parseInt(elements.valMin.value),
                valMax: parseInt(elements.valMax.value)
            },
            sizeFilter: {
                minSize: parseInt(elements.sizeMin.value),
                maxSize: parseInt(elements.sizeMax.value)
            },
            circularity: parseFloat(elements.circularity.value) / 100,
            overlapSensitivity: parseFloat(elements.overlapSensitivity.value) / 100,
            morphOperations: {
                erosion: parseInt(elements.erosion.value),
                dilation: parseInt(elements.dilation.value)
            },
            region: {
                x: parseInt(elements.regionX.value),
                y: parseInt(elements.regionY.value),
                width: parseInt(elements.regionWidth.value),
                height: parseInt(elements.regionHeight.value)
            }
        };
    }
    
    // Show/hide loading indicator
    function showLoading(show) {
        elements.previewLoading.style.display = show ? 'flex' : 'none';
    }
    
    // Add a log message
    function addLog(message, type = "") {
        const logEntry = document.createElement('div');
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        if (type) {
            logEntry.classList.add(type);
        }
        elements.logs.appendChild(logEntry);
        elements.logs.scrollTop = elements.logs.scrollHeight;
    }
    
    // Simulate detection response (for demo purposes)
    function simulateDetectionResponse() {
        // Generate a random number of cells (between 5 and 30)
        const detectedCount = Math.floor(Math.random() * 25) + 5;
        state.cellsDetected = detectedCount;
        
        // Update the UI
        elements.cellsDetected.textContent = detectedCount;
        
        // Show a sample image
        const colorName = state.cellColor === 'green' ? 'green' : 'red';
        elements.previewPlaceholder.style.display = 'none';
        elements.previewImage.src = `https://via.placeholder.com/800x600/222222/666666?text=Sample+${colorName}+cells+detection+(${detectedCount}+cells)`;
        elements.previewImage.style.display = 'block';
        
        showLoading(false);
        addLog(`Detection complete. Found ${detectedCount} ${state.cellColor} cells.`, "success");
    }
    
    // Simulate clicking process (for demo purposes)
    function simulateClickingProcess(params) {
        let clickedCount = 0;
        const clickInterval = setInterval(() => {
            if (!state.isClicking || clickedCount >= state.cellsDetected) {
                clearInterval(clickInterval);
                
                if (clickedCount >= state.cellsDetected) {
                    addLog(`Clicking complete. Clicked ${clickedCount} of ${state.cellsDetected} cells.`, "success");
                }
                
                elements.startClicking.disabled = false;
                elements.stopClicking.disabled = true;
                elements.previewDetection.disabled = false;
                state.isClicking = false;
                return;
            }
            
            clickedCount++;
            elements.cellsClicked.textContent = clickedCount;
            
            // Calculate and update success rate
            const successRate = Math.round((clickedCount / state.cellsDetected) * 100);
            elements.successRate.textContent = `${successRate}%`;
            
            addLog(`Clicked cell ${clickedCount} of ${state.cellsDetected}`, "info");
        }, 500); // Simulate clicking every 500ms
        
        state.cellsClicked = 0;
        elements.cellsClicked.textContent = "0";
        elements.successRate.textContent = "0%";
    }
    
    // Add keyboard event listener for ESC to stop clicking
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && state.isClicking) {
            handleStopClicking();
        }
    });
    
    // Initial log
    addLog("System initialized. Ready to detect and click cells.");
});
