/* LeafCare AI - Scanner Engine (Upload, Live Webcam Stream & Mobile Native Camera) */

document.addEventListener('DOMContentLoaded', () => {
  // Upload elements
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const dropzonePrompt = document.getElementById('dropzone-prompt');
  const previewContainer = document.getElementById('upload-preview-container');
  const previewImg = document.getElementById('upload-preview');
  const fileInfoBadge = document.getElementById('file-info-badge');
  const removeFileBtn = document.getElementById('remove-file-btn');
  const analyzeUploadBtn = document.getElementById('analyze-upload-btn');
  const uploadForm = document.getElementById('upload-form');

  // Camera elements
  const cameraContainer = document.getElementById('camera-container');
  const cameraVideo = document.getElementById('camera-video');
  const cameraCanvas = document.getElementById('camera-canvas');
  const cameraPlaceholder = document.getElementById('camera-placeholder');
  const cameraControls = document.getElementById('camera-controls');
  const startCameraBtn = document.getElementById('start-camera-btn');
  const directCameraBtn = document.getElementById('direct-camera-btn');
  const cameraDirectInput = document.getElementById('camera-direct-input');
  const cameraInsecureHint = document.getElementById('camera-insecure-hint');
  const stopCameraBtn = document.getElementById('stop-camera-btn');
  const captureBtn = document.getElementById('capture-btn');
  const switchCameraBtn = document.getElementById('switch-camera-btn');

  // Overlay & Error elements
  const overlay = document.getElementById('scanning-overlay');
  const scanningText = document.getElementById('scanning-status-text');
  const progressBar = document.getElementById('scanning-progress-bar');
  const errorAlert = document.getElementById('scanner-error');
  const errorMsg = document.getElementById('scanner-error-msg');

  let currentStream = null;
  let useFacingMode = 'environment'; // default to rear camera on phones
  let currentFile = null;

  // ---------------- Error Display Helper ---------------- //
  function showError(msg) {
    if (errorAlert && errorMsg) {
      errorMsg.innerHTML = msg;
      errorAlert.classList.remove('d-none');
      errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      alert(msg);
    }
  }

  function hideError() {
    if (errorAlert) {
      errorAlert.classList.add('d-none');
    }
  }

  // ---------------- Scanning Animation ---------------- //
  function showScanningOverlay(mode = 'upload') {
    if (overlay) {
      overlay.classList.remove('d-none');
      progressBar.style.width = '20%';
      scanningText.textContent = 'Preprocessing image with OpenCV...';

      setTimeout(() => {
        progressBar.style.width = '55%';
        scanningText.textContent = 'Extracting botanical features & veination...';
      }, 500);

      setTimeout(() => {
        progressBar.style.width = '85%';
        scanningText.textContent = 'MobileNetV2 neural inference across 38 classes...';
      }, 1100);
    }
  }

  function hideScanningOverlay() {
    if (overlay) {
      overlay.classList.add('d-none');
    }
  }

  // ---------------- File Upload & Drag/Drop ---------------- //
  if (dropzone && fileInput) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFileSelect(files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    });

    removeFileBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      resetFileSelection();
    });
  }

  function handleFileSelect(file) {
    hideError();
    if (!file.type.match('image.*')) {
      showError('Please select a valid image file (PNG, JPG, JPEG, WEBP).');
      return;
    }
    if (file.size > 16 * 1024 * 1024) {
      showError('File size exceeds 16MB limit.');
      return;
    }

    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      dropzonePrompt.classList.add('d-none');
      previewContainer.classList.remove('d-none');
      const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
      fileInfoBadge.textContent = `${file.name} (${sizeMb} MB)`;
      analyzeUploadBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  function resetFileSelection() {
    currentFile = null;
    fileInput.value = '';
    previewImg.src = '';
    dropzonePrompt.classList.remove('d-none');
    previewContainer.classList.add('d-none');
    analyzeUploadBtn.disabled = true;
    hideError();
  }

  // Submit Upload Form
  uploadForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentFile) {
      showError('Please choose or drop an image first.');
      return;
    }

    await submitImageFile(currentFile);
  });

  async function submitImageFile(file) {
    hideError();
    showScanningOverlay('upload');

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (response.ok && data.success) {
        progressBar.style.width = '100%';
        scanningText.textContent = 'Diagnosis complete! Preparing report...';
        setTimeout(() => {
          window.location.href = data.redirect_url;
        }, 400);
      } else {
        hideScanningOverlay();
        showError(data.error || 'Diagnosis failed. Please check the image and try again.');
      }
    } catch (err) {
      hideScanningOverlay();
      showError(`Network or server error: ${err.message}`);
    }
  }

  // ---------------- Camera Safe Detection ---------------- //
  function getMediaDevices() {
    if (typeof navigator !== 'undefined') {
      if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
        return navigator.mediaDevices;
      }
      // Check legacy prefixed implementations
      const legacyGetUserMedia = navigator.getUserMedia || 
                                 navigator.webkitGetUserMedia || 
                                 navigator.mozGetUserMedia || 
                                 navigator.msGetUserMedia;
      if (legacyGetUserMedia) {
        return {
          getUserMedia: function(constraints) {
            return new Promise((resolve, reject) => {
              legacyGetUserMedia.call(navigator, constraints, resolve, reject);
            });
          }
        };
      }
    }
    return null;
  }

  // Direct Device / Mobile Camera input button
  directCameraBtn?.addEventListener('click', () => {
    cameraDirectInput?.click();
  });

  cameraDirectInput?.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      submitImageFile(e.target.files[0]);
    }
  });

  // ---------------- Live Camera Stream Controls ---------------- //
  async function startCamera() {
    hideError();

    const mediaDevices = getMediaDevices();

    // If mediaDevices is undefined (e.g., accessed over insecure HTTP IP address)
    if (!mediaDevices) {
      if (cameraInsecureHint) {
        cameraInsecureHint.classList.remove('d-none');
      }
      
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      let guidance = `Live webcam streaming requires a <strong>Secure Context</strong> (<code>http://localhost:5000</code> or <code>https://</code>).`;
      if (!isLocalhost) {
        guidance += `<br>Since you accessed via <code>${window.location.host}</code>, browsers protect your camera. Please use <strong>"Snap Photo with Device Camera"</strong> below, or open <a href="http://localhost:5000/scanner" class="alert-link">http://localhost:5000/scanner</a> on this device.`;
      }
      showError(guidance);

      // Trigger the native device camera dialog immediately as fallback
      cameraDirectInput?.click();
      return;
    }

    try {
      if (currentStream) {
        stopCamera();
      }

      const constraints = {
        video: {
          facingMode: useFacingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      currentStream = await mediaDevices.getUserMedia(constraints);
      cameraVideo.srcObject = currentStream;
      
      cameraPlaceholder.classList.add('d-none');
      cameraContainer.classList.remove('d-none');
      cameraControls.classList.remove('d-none');
    } catch (err) {
      console.warn("Webcam error:", err);
      let errMsg = `Could not start webcam (${err.name || err.message}).`;
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errMsg = `Camera permission was denied. Please grant camera permissions in your browser bar, or tap <strong>"Snap Photo with Device Camera"</strong>.`;
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errMsg = `No webcam detected on this device. You can snap a photo with your device camera or upload a file.`;
      }
      showError(errMsg);
      cameraInsecureHint?.classList.remove('d-none');
    }
  }

  function stopCamera() {
    if (currentStream) {
      currentStream.getTracks().forEach(track => track.stop());
      currentStream = null;
    }
    cameraPlaceholder.classList.remove('d-none');
    cameraContainer.classList.add('d-none');
    cameraControls.classList.add('d-none');
  }

  startCameraBtn?.addEventListener('click', startCamera);
  stopCameraBtn?.addEventListener('click', stopCamera);

  switchCameraBtn?.addEventListener('click', () => {
    useFacingMode = (useFacingMode === 'environment') ? 'user' : 'environment';
    startCamera();
  });

  // Capture frame from live video stream
  captureBtn?.addEventListener('click', async () => {
    if (!currentStream || !cameraVideo.videoWidth) {
      showError('Camera is not ready yet.');
      return;
    }

    cameraCanvas.width = cameraVideo.videoWidth;
    cameraCanvas.height = cameraVideo.videoHeight;
    const ctx = cameraCanvas.getContext('2d');

    ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
    const base64Data = cameraCanvas.toDataURL('image/jpeg', 0.92);

    stopCamera();

    hideError();
    showScanningOverlay('camera');

    const formData = new FormData();
    formData.append('camera_image', base64Data);

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (response.ok && data.success) {
        progressBar.style.width = '100%';
        scanningText.textContent = 'Diagnosis complete! Preparing report...';
        setTimeout(() => {
          window.location.href = data.redirect_url;
        }, 400);
      } else {
        hideScanningOverlay();
        showError(data.error || 'Diagnostic evaluation failed.');
      }
    } catch (err) {
      hideScanningOverlay();
      showError(`Diagnostic communication failed: ${err.message}`);
    }
  });

  // Tab switch cleanup
  document.getElementById('upload-tab')?.addEventListener('click', () => {
    stopCamera();
    hideError();
  });
});
