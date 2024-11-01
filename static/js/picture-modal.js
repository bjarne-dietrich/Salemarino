// Enable Tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

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
                                    '<div class="container">' +
                                        '<img src="' + imageUrl + '" class="img-fluid rounded-2" id="fullSizeImage">' +
                                    '</div>' +
                                '</div>' +
                                '<div class="modal-footer">' +
                                    '<div class="container">' +
                                        '<div class="row">' +
                                            '<div class="col-auto me-auto">' +
                                                '<button type="button" class="btn btn-outline-secondary" data-placement="bottom" title="Close" data-bs-dismiss="modal">Close</button>' +
                                            '</div>' + 
                                            '<div class="col-auto">' +
                                                '<button type="button" class="btn btn-outline-danger mx-1" data-placement="bottom" title="Delete" onclick="deleteImageConfirmation(\'' + imageUrl + '\')"><i class="bi-trash3"></i></button>' +
                                                '<button type="button" class="btn btn-outline-primary mx-1 edit-button" data-placement="bottom" title="Edit Comment" onclick="editComment(\'' + imageUrl + '\')"><i class="bi bi-pencil-fill"></i></button>' +
                                                '<button type="button" class="btn btn-outline-primary mx-1" data-placement="bottom" title="Download" onclick="openInNewTab(\'' + imageUrl + '?attached=true\')"><i class="bi bi-cloud-download"></i></button>' +
                                                '<button type="button" class="btn btn-outline-primary mx-1" data-placement="bottom" title="Open in new Tab" onclick="openInNewTab(\'' + imageUrl + '\')"><i class="bi bi-box-arrow-up-right"></i></button>' +
                                            '</div>' + 
                                        '</div>' +
                                    '</div>' +
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
        
        // Close the modal after deletion
        var modal = bootstrap.Modal.getInstance(document.querySelector('.modal'));
        modal.hide();
        setTimeout(function(){
            window.location.reload();
         }, 500);
        
    } else {
        // User canceled deletion
        console.log('Deletion canceled by user.');
    }
}

// JavaScript function to edit the comment
function editComment(imageUrl) {
    // Prompt the user to enter a new comment
    var newComment = prompt("Enter new comment:");
    if (newComment !== null) {
        // If the user entered a new comment (not canceled), send an AJAX request to update the comment in the database
        var filename = imageUrl.split('/').pop(); // Extract filename from the URL
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/edit_comment", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    // Comment successfully updated, reload the page or update the comment text on the page dynamically
                    console.log('Comment updated successfully for image:', imageUrl);
                    // You can add your code here to update the comment text on the page dynamically if needed
                    location.reload(); // Reload the page to reflect changes
                } else {
                    console.error('Error updating comment for image:', imageUrl);
                    alert('Error updating comment. Please try again.');
                }
            }
        };
        xhr.send(JSON.stringify({ filename: filename, comment: newComment }));
    }
}
