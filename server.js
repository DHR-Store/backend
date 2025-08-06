// my-update-server/server.js

const express = require('express');
const app = express();
const port = 3000; // You can change this port

// Middleware to parse JSON bodies
app.use(express.json());

// Hardcoded release data for demonstration purposes.
// In a real application, you would fetch this from a database.
const releases = [
  {
    version: "3.2.5", // Latest version
    releaseNotes: "Exciting new features!\n- Added dark mode support\n- Improved performance for large lists",
    downloadUrl: "http://localhost:3000/downloads/your-app-v1.0.2.apk", // IMPORTANT: Update this URL to your actual hosted APK
    fileName: "your-app-v1.0.2.apk",
    publishedAt: "2025-08-06T12:00:00Z"
  },
  {
    version: "1.0.1",
    releaseNotes: "Bug fixes and performance improvements.\n- Fixed login issue\n- Improved UI responsiveness",
    downloadUrl: "http://localhost:3000/downloads/your-app-v1.0.1.apk",
    fileName: "your-app-v1.0.1.apk",
    publishedAt: "2025-08-01T10:00:00Z"
  },
  {
    version: "1.0.0",
    releaseNotes: "Initial release.",
    downloadUrl: "http://localhost:3000/downloads/your-app-v1.0.0.apk",
    fileName: "your-app-v1.0.0.apk",
    publishedAt: "2025-07-20T09:00:00Z"
  }
];

// Endpoint to get the latest release information
app.get('/api/latest-release', (req, res) => {
  console.log('Request received for /api/latest-release');
  // In a real scenario, you'd query your database to find the actual latest release.
  // Here, we just return the first one in our hardcoded array, assuming it's the latest.
  if (releases.length > 0) {
    res.json(releases[0]);
  } else {
    res.status(404).json({ message: "No releases found." });
  }
});

// Serve static files (like your APKs).
// In a production environment, you'd typically use a dedicated file storage service (e.g., AWS S3, Google Cloud Storage)
// and provide direct download URLs from there, rather than serving directly from your API server.
app.use('/downloads', express.static('downloads')); // This assumes you have a 'downloads' folder in your server root

// Start the server
app.listen(port, () => {
  console.log(`Update API server listening at http://localhost:${port}`);
  console.log('Make sure to place your APK files in the "downloads" folder.');
});

