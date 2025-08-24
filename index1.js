document.getElementById('registerForm').addEventListener('submit', function(e) {
  e.preventDefault(); // फॉर्म का डिफ़ॉल्ट सबमिट रोकें
  
  const aadhaar = document.getElementById('aadhaarInput').value;
  const phone = document.getElementById('phoneInput').value;

  if (aadhaar.length !== 12 || phone.length !== 10) {
    alert('कृपया सही आधार और फोन नंबर डालें।');
    return;
  }

  // किसान प्रोफाइल लोड करना
  loadFarmerProfile(aadhaar);
});