// my-update-server/server.js (or index.js)

const express = require('express');
const app = express();
// Vercel will assign its own port, so we don't need to listen on a specific port here
// const port = 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// Hardcoded release data for demonstration purposes.
// In a real application, you would fetch this from a database.
const releases = [
  {
    version: "3.2.5", // Latest version
    releaseNotes: "Exciting new features!\n- Added dark mode support\n- Improved performance for large lists",
    // IMPORTANT: Update this URL to your Vercel domain + /downloads/your-app-v1.0.2.apk
    // For now, you can leave it as a placeholder or adjust after deployment.
    // If you plan to host APKs on Vercel, you'll need to configure static file serving or use a dedicated storage service.
    // For simplicity, let's assume you'll host APKs elsewhere (e.g., GitHub Releases, S3, etc.)
    // or adjust this URL after you get your Vercel domain.
    downloadUrl: "https://your-vercel-app-domain.vercel.app/downloads/your-app-v1.0.2.apk",
    fileName: "your-app-v1.0.2.apk",
    publishedAt: "2025-08-06T12:00:00Z"
  },
  {
    version: "1.0.1",
    releaseNotes: "Bug fixes and performance improvements.\n- Fixed login issue\n- Improved UI responsiveness",
    downloadUrl: "https://your-vercel-app-domain.vercel.app/downloads/your-app-v1.0.1.apk",
    fileName: "your-app-v1.0.1.apk",
    publishedAt: "2025-08-01T10:00:00Z"
  }
];

// Endpoint to get the latest release information
app.get('/api/latest-release', (req, res) => {
  console.log('Request received for /api/latest-release');
  if (releases.length > 0) {
    res.json(releases[0]);
  } else {
    res.status(404).json({ message: "No releases found." });
  }
});

// If you want to serve static files (like APKs) directly from Vercel,
// you'd typically place them in a 'public' directory and Vercel serves them automatically.
// The `app.use('/downloads', express.static('downloads'))` line is more for local Express servers.
// For Vercel, you'd usually put APKs directly in a `public` folder in your project root,
// or use a dedicated file storage service (like GitHub Releases, AWS S3, Google Cloud Storage).
// For this example, we'll assume the `downloadUrl` points to an external host for APKs.

// Export the app for Vercel
module.exports = app;

// Comment out the app.listen part as Vercel handles the server listening internally
// app.listen(port, () => {
//   console.log(`Update API server listening at http://localhost:${port}`);
//   console.log('Make sure to place your APK files in the "downloads" folder.');
// });