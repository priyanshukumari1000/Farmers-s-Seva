document.getElementById("cropForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    N: parseFloat(document.getElementById("n").value),
    P: parseFloat(document.getElementById("p").value),
    K: parseFloat(document.getElementById("k").value),
    temperature: parseFloat(document.getElementById("temp").value),
    humidity: parseFloat(document.getElementById("humidity").value),
    ph: parseFloat(document.getElementById("ph").value),
    rainfall: parseFloat(document.getElementById("rain").value)
  };

  const response = await fetch("http://localhost:5000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  const result = await response.json();
  document.getElementById("result").innerText = "Recommended Crop: " + result.recommended_crop;
});














const form = document.getElementById('cropForm');
const resultDiv = document.getElementById('result');

form.addEventListener('submit', async function (e) {
  e.preventDefault();

  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  // Convert string inputs to float
  for (let key in data) {
    data[key] = parseFloat(data[key]);
  }

  const response = await fetch('/predict_crop', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  const result = await response.json();
  resultDiv.innerHTML = `<h3>Recommended Crop: ${result.prediction}</h3>`;
});
