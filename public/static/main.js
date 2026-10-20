document.addEventListener("click", async (event) => {
  const button = event.target.closest(".delete-post");
  if (!button) return;
  const error = document.getElementById("delete-error");
  button.disabled = true;
  try {
    const response = await fetch(button.dataset.deleteUrl, { credentials: "same-origin" });
    const result = await response.json();
    if (!response.ok || result.status !== 1) throw new Error(result.message || "Could not delete post.");
    window.location.reload();
  } catch (failure) {
    error.textContent = failure.message;
    error.hidden = false;
    button.disabled = false;
  }
});
