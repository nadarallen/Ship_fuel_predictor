document.getElementById('prediction-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = document.getElementById('predict-btn');
    const resultContainer = document.getElementById('result-container');
    const fuelResult = document.getElementById('fuel-result');
    const originalBtnText = submitBtn.innerHTML;

    // Loading state
    submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Calculating...';
    submitBtn.disabled = true;

    // Collect data
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        // Convert numbers
        if (key !== 'ship_type') {
            data[key] = parseFloat(value);
        } else {
            data[key] = value;
        }
    });

    try {
        const response = await fetch('/predict_fuel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            // Animate result value
            resultContainer.classList.remove('hidden');
            // Small delay to allow display block to apply before adding visible class for transition
            setTimeout(() => {
                resultContainer.classList.add('visible');
            }, 10);
            
            animateValue(fuelResult, 0, result.predicted_fuel_liters, 1000);
        } else {
            alert('Error: ' + (result.error || 'Unknown error occurred'));
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to the server.');
    } finally {
        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;
    }
});

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            // Ensure exact final value with decimal if needed, though int is usually fine for liters
             obj.innerHTML = end.toLocaleString();
        }
    };
    window.requestAnimationFrame(step);
}
