let currentStep = 1;
const totalSteps = 6;
const profileData = {};

document.addEventListener('DOMContentLoaded', () => {
    updateProgress();
});

// Navigation Logic
function nextStep(step) {
    if (!validateStep(step)) return;

    // Collect data for current step
    collectData(step);

    // Transition
    document.getElementById(`step${step}`).style.display = 'none';
    document.getElementById(`step${step + 1}`).style.display = 'block';
    document.getElementById(`step${step + 1}`).classList.add('active');

    currentStep++;
    updateProgress();

    // Scroll to top
    window.scrollTo(0, 0);
}

function prevStep(step) {
    document.getElementById(`step${step}`).style.display = 'none';
    document.getElementById(`step${step - 1}`).style.display = 'block';

    currentStep--;
    updateProgress();
}

function updateProgress() {
    document.querySelectorAll('.step-dot').forEach(dot => {
        const num = parseInt(dot.getAttribute('data-step'));
        dot.classList.remove('active', 'completed');
        if (num === currentStep) dot.classList.add('active');
        if (num < currentStep) dot.classList.add('completed');
    });
}

// Data Collection & Validation
function collectData(step) {
    const section = document.getElementById(`step${step}`);
    const inputs = section.querySelectorAll('input, select');

    inputs.forEach(input => {
        if (input.name) {
            profileData[input.name] = input.value;
        }
    });

    console.log("Current Profile Data:", profileData);
}

function validateStep(step) {
    const section = document.getElementById(`step${step}`);
    const required = section.querySelectorAll('[required]');
    let valid = true;

    required.forEach(input => {
        if (!input.value) {
            input.style.borderColor = '#ff4444';
            valid = false;
            // Shake effect
            input.animate([
                { transform: 'translateX(0)' },
                { transform: 'translateX(10px)' },
                { transform: 'translateX(-10px)' },
                { transform: 'translateX(0)' }
            ], { duration: 300 });
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    });

    return valid;
}

// UI Interactions
function selectOption(fieldName, value, cardElement) {
    // Hidden input update
    const input = document.querySelector(`input[name="${fieldName}"]`);
    if (input) input.value = value;

    // Visual feedback
    // Find parent container to clear siblings
    const parent = cardElement.parentElement;
    parent.querySelectorAll('.selection-card').forEach(c => c.classList.remove('selected'));
    cardElement.classList.add('selected');
}

function toggleSelection(cardElement, fieldName) {
    // Multi-select logic would go here, simplifying to visual toggle for now
    cardElement.classList.toggle('selected');
    // In a real implementation, we'd update a hidden array input
}

// Scientific Calculations
function calculateScientificMetrics() {
    const p = profileData;

    // 1. BMI
    const heightM = p.height / 100;
    const bmi = (p.weight / (heightM * heightM)).toFixed(1);

    // 2. BMR (Mifflin-St Jeor)
    // Men: (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
    // Women: (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
    let bmr = (10 * p.weight) + (6.25 * p.height) - (5 * p.age);
    bmr += (p.gender === 'Male') ? 5 : -161;

    // 3. TDEE (Activity Multiplier)
    const multipliers = {
        'Sedentary': 1.2,
        'Active': 1.55
    };
    // Default to sedentary if undefined, simplified logic for wizard demo
    const activityMult = multipliers[p.job_activity] || 1.375;
    const tdee = Math.round(bmr * activityMult);

    return { bmi, bmr, tdee };
}

async function submitProfile() {
    // Final data collection
    collectData(currentStep);

    const metrics = calculateScientificMetrics();
    const finalProfile = { ...profileData, ...metrics };

    try {
        // Use new MongoDB auth endpoint
        const response = await fetch('/api/auth/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(finalProfile)
        });

        const result = await response.json();

        if (result.error) {
            if (result.error.includes('Login')) {
                alert('Please login first to save your profile');
                window.location.href = '/login';
                return;
            }
            throw new Error(result.error);
        }

        if (result.success) {
            alert('Scientific Profile Created! Redirecting to Diet Planner...');
            window.location.href = '/diet/create';
        } else {
            alert('Error saving profile: ' + (result.message || 'Unknown error'));
        }
    } catch (e) {
        console.error("Submission error:", e);
        alert("Error: " + e.message);
    }
}
