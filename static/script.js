document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('upload-form')) {
        setupUploadForm();
    }
    if (document.getElementById('gallery-container')) {
        setupGallery();
    }
    registerServiceWorker();
});

function setupUploadForm() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const commentInput = document.getElementById('comment-input');
    const loading = document.getElementById('loading');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Please select an image first');
            return;
        }

        loading.classList.remove('hidden');
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('comment', commentInput.value);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                window.location.href = '/gallery';
            } else {
                alert('Upload failed. Please try again.');
            }
        } catch (error) {
            alert('Error uploading file: ' + error.message);
        } finally {
            loading.classList.add('hidden');
        }
    });
}

function setupGallery() {
    const galleryContainer = document.getElementById('gallery-container');
    
    function updateGallery() {
        fetch('/api/images')
            .then(response => response.json())
            .then(images => {
                galleryContainer.innerHTML = '';
                
                images.forEach(image => {
                    if (image.status === 'expired') return;
                    
                    const item = document.createElement('div');
                    item.className = `gallery-item ${image.status}`;
                    
                    const img = document.createElement('img');
                    img.src = `/uploads/${image.filename}`;
                    img.alt = image.comment;
                    
                    const comment = document.createElement('div');
                    comment.className = 'comment';
                    comment.textContent = image.comment;
                    
                    item.appendChild(img);
                    item.appendChild(comment);
                    galleryContainer.appendChild(item);
                });
            })
            .catch(error => console.error('Error fetching images:', error));
    }
    
    updateGallery();
    setInterval(updateGallery, 2000); // Update every 2 seconds
}

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('ServiceWorker registration successful');
                })
                .catch(err => {
                    console.log('ServiceWorker registration failed: ', err);
                });
        });
    }
}
