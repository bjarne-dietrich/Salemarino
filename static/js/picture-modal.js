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
                                    '<button type="button" class="btn btn-primary" onclick="openInNewTab(\'' + imageUrl + '\')">Open in New Tab</button>' +
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