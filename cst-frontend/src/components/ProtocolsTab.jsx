import { useState } from 'react';

export default function ProtocolsTab() {
    // State to store selected files for upload
    const [files, setFiles] = useState(null);
    // State to store API response from upload
    const [response, setResponse] = useState(null);
    // State to track loading status during upload
    const [loading, setLoading] = useState(false);

    // Handle file upload to the backend API
    const handleUpload = async () => {
        // Early return if no files selected
        if (!files) return;

        // Set loading state to true
        setLoading(true);
        
        // Create FormData object to hold files
        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        try {
            // Send POST request to backend API with files
            const res = await fetch('http://localhost:8000/api/protocols/upload', {
                method: 'POST',
                body: formData
            });
            
            // Parse JSON response from server
            const data = await res.json();
            setResponse(data);
        } catch (err) {
            // Log error if upload fails
            console.error('Upload failed:', err);
        }
        
        // Reset loading state
        setLoading(false);
    };

    // Render UI with file input and upload button
    return (
        <div>
            <h2>Upload Protocols</h2>
            
            {/* File input for selecting multiple protocol files */}
            <input 
                type="file" 
                multiple 
                onChange={(e) => setFiles(e.target.files)}
            />
            
            {/* Upload button - disabled during upload, shows loading state */}
            <button onClick={handleUpload} disabled={loading}>
                {loading ? 'Uploading...' : 'Upload'}
            </button>
            
            {/* Display server response if available */}
            {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
        </div>
    );
}
 