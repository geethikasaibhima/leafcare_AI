/* LeafCare AI - Scanner Engine (Upload & Live Webcam Stream) */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
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
      errorMsg.textContent = msg;
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
      }, 600);

      setTimeout(() => {
        progressBar.style.width = '85%';
        scanningText.textContent = 'MobileNetV2 neural inference across 38 classes...';
      }, 1300);
    }
  }

  function hideScanningOverlay() {
    if (overlay) {
      overlay.classList.add('d-none');
    }
  }

  // ---------------- File Upload & Drag/Drop ---------------- //
  if (dropzone && fileInput) {
    // Drag events
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
    // Validate image mime type
    if (!file.type.match('image.*')) {
      showError('Please select a valid image file (PNG, JPG, JPEG, WEBP).');
      return;
    }
    // Size limit 16MB
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

    hideError();
    showScanningOverlay('upload');

    const formData = new FormData();
    formData.append('image', currentFile);

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
  });

  // ---------------- Camera Controls ---------------- //
  async function startCamera() {
    hideError();
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

      currentStream = await navigator.mediaDevices.getUserMedia(constraints);
      cameraVideo.srcObject = currentStream;
      
      cameraPlaceholder.classList.add('d-none');
      cameraContainer.classList.remove('d-none');
      cameraControls.classList.remove('d-none');
    } catch (err) {
      showError(`Camera access could not be initialized: ${err.message}. Please allow camera permissions or use file upload.`);
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

  // Capture frame from video stream
  captureBtn?.addEventListener('click', async () => {
    if (!currentStream || !cameraVideo.videoWidth) {
      showError('Camera is not ready yet.');
      return;
    }

    // Set canvas dimensions matching video
    cameraCanvas.width = cameraVideo.videoWidth;
    cameraCanvas.height = cameraVideo.videoHeight;
    const ctx = cameraCanvas.getContext('2d');

    // Draw un-mirrored frame
    ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
    const base64Data = cameraCanvas.toDataURL('image/jpeg', 0.92);

    // Stop camera stream
    stopCamera();

    // Send frame to server
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

  // Cleanup on tab switch
  document.getElementById('upload-tab')?.addEventListener('click', () => {
    stopCamera();
    hideError();
  });
});
