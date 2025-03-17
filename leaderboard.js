const JSON_URL = 'leaderboard.json';
const REFRESH_INTERVAL = 300000; // Refresh every 5 minutes
const INACTIVITY_THRESHOLD_MINUTES = 15; // Consider stream inactive after 15 minutes of no updates

// Function to fetch and update leaderboard
async function updateLeaderboard() {
    try {
        const response = await fetch(`${JSON_URL}?t=${Date.now()}`); // Add timestamp to prevent caching
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Update stream status indicator
        const statusElement = document.getElementById('status');
        if (data.status === 'active') {
            statusElement.textContent = 'STREAM ACTIVE';
            statusElement.className = 'status-indicator active';
            
            // Update positions with data
            data.users.forEach(user => {
                const position = document.getElementById(`position-${user.position}`);
                if (position) {
                    position.querySelector('.username').textContent = user.username;
                    position.querySelector('.points').textContent = user.points;
                }
            });
        } else {
            statusElement.textContent = 'STREAM OFFLINE';
            statusElement.className = 'status-indicator inactive';
            
            // Clear all positions if stream is inactive
            clearLeaderboard();
        }
        
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        
        // Handle connection errors by marking stream as offline
        const statusElement = document.getElementById('status');
        statusElement.textContent = 'CONNECTION ERROR';
        statusElement.className = 'status-indicator inactive';
    }
}

// Function to clear the leaderboard
function clearLeaderboard() {
    for (let i = 1; i <= 25; i++) {
        const position = document.getElementById(`position-${i}`);
        if (position) {
            position.querySelector('.username').textContent = '';
            position.querySelector('.points').textContent = '';
        }
    }
}

// Initial update
document.addEventListener('DOMContentLoaded', function() {
    updateLeaderboard();
    
    // Set up periodic refresh
    setInterval(updateLeaderboard, REFRESH_INTERVAL);
});