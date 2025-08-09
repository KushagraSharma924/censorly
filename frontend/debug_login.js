// Debug version of login function
// Add this to your browser console to test login directly

async function debugLogin() {
  const loginData = {
    email: "kush090605@gmail.com",
    password: "kush1234"
  };

  console.log('🚀 Starting login test...');
  console.log('📝 Login data:', loginData);
  console.log('🌐 API URL:', 'https://ai-profanity-filter.onrender.com/api/auth/login');

  try {
    const response = await fetch('https://ai-profanity-filter.onrender.com/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'omit',
      body: JSON.stringify(loginData),
    });

    console.log('📡 Response status:', response.status);
    console.log('📡 Response ok:', response.ok);
    console.log('📡 Response headers:', [...response.headers.entries()]);

    const data = await response.json();
    console.log('📄 Response data:', data);

    if (response.ok) {
      console.log('✅ Login successful!');
      return data;
    } else {
      console.log('❌ Login failed:', data.error);
      return null;
    }
  } catch (error) {
    console.error('💥 Network error:', error);
    return null;
  }
}

// Run the test
debugLogin();
