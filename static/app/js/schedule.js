function openEditModal(worker_id, name, email, mobile,experience) {
    document.getElementById('worker_id').value = worker_id;
    document.getElementById('editName').value = name;
    document.getElementById('editEmail').value = email;
    document.getElementById('editPhone').value = mobile;
    document.getElementById('editExperience').value = experience;
    document.getElementById('editModal').classList.remove('hidden');
}

function openAddModal(worker_id, name, email, mobile,experience) {
    document.getElementById('worker_id').value = worker_id;
    document.getElementById('editName').value = name;
    document.getElementById('editEmail').value = email;
    document.getElementById('editPhone').value = mobile;
    document.getElementById('editExperience').value = experience;
    document.getElementById('addModal').classList.remove('hidden');
}
document.getElementById('editEmail').addEventListener('input', function () {
    let emailField = document.getElementById('editEmail');
    let emailError = document.getElementById('emailError');
    let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (emailField.value.match(emailPattern)) {
        emailError.style.display = 'none';
    } else {
        emailError.style.display = 'block';
    }
});

function closeEditModal() {
    document.getElementById('worker_id').value = '';
    document.getElementById('editName').value = '';
    document.getElementById('editEmail').value = '';
    document.getElementById('editPhone').value = '';
    document.getElementById('editExperience').value = '';
    document.getElementById('editModal').classList.add('hidden');
}
function closeAddModal() {
    document.getElementById('addName').value = '';
    document.getElementById('addEmail').value = '';
    document.getElementById('addPhone').value = '';
    document.getElementById('editExperience').value = '';
    document.getElementById('addModal').classList.add('hidden');
}
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function () {
        const output = document.getElementById('profileImage');
        output.src = reader.result;
    }
    reader.readAsDataURL(event.target.files[0]);
}

function saveProfile() {
    const name = document.getElementById('editName').value;
    const email = document.getElementById('editEmail').value;
    const phone = document.getElementById('editPhone').value;
    document.getElementById('profileName').innerText = name || "Please enter your name";
    document.getElementById('profileEmail').innerText = email || "Please enter your email";
    document.getElementById('profilePhone').innerText = phone || "Please enter your mobile";
    closeEditModal();
}