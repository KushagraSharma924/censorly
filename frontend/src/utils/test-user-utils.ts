// Test script to verify user utilities work correctly
import { getProfileImageUrl, getUserInitials, getUserDisplayName, formatUserData } from '../lib/user-utils';

// Test cases
const testCases = [
  null,
  undefined,
  {},
  { email: '' },
  { email: 'test@example.com' },
  { email: 'test@example.com', name: 'John Doe' },
  { email: 'test@example.com', full_name: 'Jane Smith' },
  { email: 'test@example.com', name: '', full_name: '' },
];

console.log('Testing user utilities:');

testCases.forEach((testCase, index) => {
  console.log(`\n--- Test Case ${index + 1}: ---`);
  console.log('Input:', testCase);
  
  try {
    const formatted = formatUserData(testCase);
    console.log('Formatted:', formatted);
    
    const imageUrl = getProfileImageUrl(formatted);
    console.log('Image URL:', imageUrl);
    
    const initials = getUserInitials(formatted);
    console.log('Initials:', initials);
    
    const displayName = getUserDisplayName(formatted);
    console.log('Display Name:', displayName);
  } catch (error) {
    console.error('Error:', error);
  }
});
