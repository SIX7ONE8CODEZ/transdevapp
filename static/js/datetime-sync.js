/**
 * Date and Time Synchronization Functions for TransDev Scheduler
 * Handles auto-adjustment of end times when start times are changed
 * to maintain the original duration
 */

/**
 * Parse a datetime string into a JavaScript Date object
 * Handles multiple formats
 * 
 * @param {string} dateStr - Date string to parse
 * @return {Date|null} - JavaScript Date object or null if invalid
 */
function parseDateTime(dateStr) {
    if (!dateStr) return null;
    
    // Handle Date objects
    if (dateStr instanceof Date) return dateStr;
    
    // Try different formats
    const formats = [
        // ISO format
        str => new Date(str),
        // US format with AM/PM
        str => {
            const parts = str.match(/(\d{2})\/(\d{2})\/(\d{4}) (\d{1,2}):(\d{2}) ([AP]M)/i);
            if (parts) {
                let hour = parseInt(parts[4]);
                const minute = parseInt(parts[5]);
                const ampm = parts[6].toUpperCase();
                if (ampm === "PM" && hour < 12) hour += 12;
                if (ampm === "AM" && hour === 12) hour = 0;
                return new Date(parts[3], parts[1] - 1, parts[2], hour, minute);
            }
            return null;
        },
        // 24-hour format
        str => {
            const parts = str.match(/(\d{2})\/(\d{2})\/(\d{4}) (\d{2}):(\d{2})/i);
            if (parts) {
                return new Date(parts[3], parts[1] - 1, parts[2], parts[4], parts[5]);
            }
            return null;
        }
    ];
    
    for (const formatFn of formats) {
        try {
            const date = formatFn(dateStr);
            if (date && !isNaN(date.getTime())) {
                return date;
            }
        } catch (e) {
            // Try next format
        }
    }
    
    console.error("Failed to parse date:", dateStr);
    return null;
}

/**
 * Format a date object as a string
 * 
 * @param {Date|string} dateObj - Date to format
 * @returns {string} - Formatted date string
 */
function formatDateTime(dateObj) {
    if (!dateObj) return '';
    
    // Try to convert to a Date object if it's a string
    if (typeof dateObj === 'string') {
        dateObj = parseDateTime(dateObj);
    }
    
    if (!dateObj || isNaN(dateObj.getTime())) return '';
    
    return dateObj.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

/**
 * Calculate duration between two dates in milliseconds
 * 
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @returns {number} - Duration in milliseconds, defaults to 1 hour if calculation fails
 */
function calculateDuration(startDate, endDate) {
    // Default to 1 hour (3600000 ms)
    const DEFAULT_DURATION = 3600000;
    
    if (!startDate || !endDate || isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        return DEFAULT_DURATION;
    }
    
    const duration = endDate.getTime() - startDate.getTime();
    
    // If somehow end is before start or duration is invalid, return default
    return duration > 0 ? duration : DEFAULT_DURATION;
}

/**
 * Show a notification message to the user
 * 
 * @param {string} message - Message to display
 * @param {string} type - Message type (success, error, info)
 */
function showDateTimeNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    notification.textContent = message;
    notification.className = 'notification ' + type;
    notification.classList.remove('hidden');
    
    // Hide after 5 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}
