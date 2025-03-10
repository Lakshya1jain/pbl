import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [file, setFile] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setModelUrl(`http://localhost:5000${response.data.model_url}`);
    } catch (error) {
      console.error("Upload failed", error);
    }
    setLoading(false);
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>Blueprint to 3D Model</h2>
      <input type="file" onChange={handleFileChange} accept="image/*" />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload & Generate 3D Model"}
      </button>
      {modelUrl && (
        <div>
          <h3>Download Your 3D Model</h3>
          <a href={modelUrl} download>Download Blender Model</a>
        </div>
      )}
    </div>
  );
};

export default App;
