// Open Image Preview
function openImagePreview(src) {
    document.getElementById("imagePreview").src = src;
    document.getElementById("imagePreviewModal").style.display = "flex";
    centerModal("imagePreviewModal");
}

// Close Image Preview
function closeImagePreview() {
    document.getElementById("imagePreviewModal").style.display = "none";
}

// Open PDF Preview
function openPdfPreview(fileUrl) {
    document.getElementById("pdfPreview").src = fileUrl;
    document.getElementById("pdfPreviewModal").style.display = "flex";
    centerModal("pdfPreviewModal");
}

// Close PDF Preview
function closePdfPreview() {
    document.getElementById("pdfPreviewModal").style.display = "none";
}

// Open Text/CSV Preview
function openTextPreview(fileUrl) {
    fetch(fileUrl)
        .then(response => response.text())
        .then(text => {
            document.getElementById("textPreviewContent").textContent = text;
            document.getElementById("textPreviewModal").style.display = "flex";
            centerModal("textPreviewModal");
        });
}

// Close Text Preview
function closeTextPreview() {
    document.getElementById("textPreviewModal").style.display = "none";
}

// Close modal when clicking outside the content box
function closeModal(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = "none";
    }
}

// Center modal on the webpage
function centerModal(modalId) {
    const modal = document.getElementById(modalId);
    const rect = modal.getBoundingClientRect();
    modal.style.top = `calc(50% - ${rect.height / 2}px)`;
    modal.style.left = `calc(50% - ${rect.width / 2}px)`;
}

// Show popup message
function showPopupMessage(message) {
    const popup = document.getElementById("popupMessage");
    popup.textContent = message;
    popup.style.display = "block";
    setTimeout(() => {
        popup.style.display = "none";
    }, 3000);
}

// Handle file upload form submission
document.getElementById("uploadForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch(this.action, {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            showPopupMessage("File uploaded successfully!");
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showPopupMessage("File upload failed!");
        }
    }).catch(error => {
        showPopupMessage("File upload failed!");
    });
});
