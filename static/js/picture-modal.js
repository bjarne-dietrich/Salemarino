// JavaScript function to delete an image
function deleteImage(imageUrl) {
    // Display a confirmation dialog
    var confirmation = confirm("Are you sure you want to delete this image?");
    if (confirmation) {
        // User confirmed deletion
        // You can add your code here to delete the image
        console.log('Deleting image:', imageUrl);
        // Optionally, you may close the modal after deletion
        var modal = bootstrap.Modal.getInstance(document.querySelector('.modal'));
        modal.hide();
    } else {
        // User canceled deletion
        console.log('Deletion canceled by user.');
    }
}

function showModal(imageUrl) {
    var existingModal = document.querySelector('.modal');
    if (existingModal) {
        existingModal.remove();
    }
    // Create a modal with the thumbnail image
    var modalHtml = '<div class="modal" tabindex="-1" role="dialog">' +
                        '<div class="modal-dialog" role="document">' +
                            '<div class="modal-content">' +
                                '<div class="modal-body">' +
                                    '<img src="' + imageUrl + '" class="img-fluid" id="fullSizeImage">' +
                                '</div>' +
                                '<div class="modal-footer">' +
                                    '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>' +
                                    '<button type="button" class="btn btn-danger" onclick="deleteImageConfirmation(\'' + imageUrl + '\')">Delete</button>' +
                                    '<button type="button" class="btn btn-primary" onclick="openInNewTab(\'' + imageUrl + '?attached=true\')">Download</button>' +
                                    '<button type="button" class="btn btn-primary" onclick="openInNewTab(\'' + imageUrl + '\')">Open</button>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</div>';
    document.body.insertAdjacentHTML('beforeend', modalHtml);  // Insert the modal into the document
    var modal = new bootstrap.Modal(document.querySelector('.modal'));  // Initialize modal
    modal.show();  // Show the modal
}

// JavaScript function to open an image in a new tab
function openInNewTab(imageUrl) {
    if (imageUrl) { 
        window.open(imageUrl, '_blank');
    }
}

// JavaScript function to delete an image with confirmation dialog
function deleteImageConfirmation(imageUrl) {
    // Display a confirmation dialog
    var confirmation = confirm("Are you sure you want to delete this image?");
    if (confirmation) {
        // User confirmed deletion
        // You can add your code here to delete the image file
        console.log('Deleting image:', imageUrl);

        // Delete image from the database
        var filename = imageUrl.split('/').pop(); // Extract filename from the URL
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/delete_image", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    // Image successfully deleted, reload the search page
                    location.reload();
                } else {
                    console.error('Error deleting image:', xhr.responseText);
                    alert('Error deleting image. Please try again.');
                }
            }
        };
        xhr.send(JSON.stringify({filename: filename}));
        
        // Optionally, you may close the modal after deletion
        var modal = bootstrap.Modal.getInstance(document.querySelector('.modal'));
        modal.hide();
    } else {
        // User canceled deletion
        console.log('Deletion canceled by user.');
    }
}
