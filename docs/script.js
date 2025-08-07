// Simple client-side script to open a pre-filled GitHub Issue URL
// No tokens needed – user must be signed in to GitHub in the browser.
const repo = "wTaylorBickelmann/trello_chat_app";
const label = "daily-input";

document.getElementById("createIssue").addEventListener("click", () => {
  const text = document.getElementById("taskInput").value.trim();
  if (!text) {
    alert("Please enter something first.");
    return;
  }
  const today = new Date().toISOString().slice(0, 10);
  const title = encodeURIComponent(`Tasks for ${today}`);
  const body = encodeURIComponent(text);
  const url = `https://github.com/${repo}/issues/new?labels=${label}&title=${title}&body=${body}`;
  window.open(url, "_blank");
});
