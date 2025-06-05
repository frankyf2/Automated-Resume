function openPopup(jobId, jobTitle) {
    document.getElementById("applyPopup").classList.add("active");
    document.getElementById("popupJobId").value = jobId;
    document.getElementById("popupJobTitle").innerText = jobTitle;
}

function closePopup() {
    document.getElementById("applyPopup").classList.remove("active");
}

document.getElementById("applicationForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent the default form submission

    let formData = new FormData(this);

    fetch("/recruit/", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);  // Show success message
            closePopup();  // Close the pop-up after submission
            document.getElementById("applicationForm").reset(); // Clear the form
        } else {
            alert("Error: " + data.message);  // Show error message if any
        }
    })
    .catch(error => console.error("Error:", error));
});