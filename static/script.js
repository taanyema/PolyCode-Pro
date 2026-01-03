function sendImage() {
  const input = document.getElementById("imageInput");

  if (!input.files.length) {
    alert("Choisis une image");
    return;
  }

  const formData = new FormData();
  formData.append("image", input.files[0]);

  fetch("/image", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    addMessage("bot", data.reply);
  });
}