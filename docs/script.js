// Simple client-side script to open a pre-filled GitHub Issue URL
// No tokens needed – user must be signed in to GitHub in the browser.
const repo = "wTaylorBickelmann/trello_chat_app";
const label = "daily-input";

// Utility to retrieve/store GitHub PAT in localStorage
function getGithubToken(scopeHint = "public_repo") {
  const existing = localStorage.getItem("gh_pat");
  let token = existing;
  if (!token) {
    token = prompt(`Enter a GitHub Personal Access Token with '${scopeHint}' scope (stored in your browser)`)?.trim();
    if (!token) return null;
    localStorage.setItem("gh_pat", token);
  }
  return token;
}

// Create a GitHub issue via REST API instead of opening a new browser tab
async function createGithubIssue() {
  const text = document.getElementById("taskInput").value.trim();
  if (!text) {
    alert("Please enter something first.");
    return;
  }
  const today = new Date().toISOString().slice(0, 10);
  const title = `Tasks for ${today}`;
  const token = getGithubToken("public_repo");
  if (!token) return;

  const res = await fetch(`https://api.github.com/repos/${repo}/issues`, {
    method: "POST",
    headers: {
      "Authorization": `token ${token}`,
      "Accept": "application/vnd.github+json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ title, body: text, labels: [label] })
  });

  if (res.ok) {
    alert("GitHub issue created!");
  } else {
    const msg = await res.text();
    alert("Failed to create issue: " + msg);
  }
}

document.getElementById("createIssue").addEventListener("click", createGithubIssue);

// Trigger GitHub Actions workflow via API (requires a PAT with 'workflow' scope)
async function triggerWorkflow() {
  const token = getGithubToken("workflow");
  if (!token) return;
  const res = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/nightly.yml/dispatches`, {
    method: "POST",
    headers: {
      "Authorization": `token ${token}`,
      "Accept": "application/vnd.github+json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ ref: "main" })
  });
  if (res.ok) {
    alert("Workflow triggered! Check Actions tab.");
  } else {
    const msg = await res.text();
    alert("Failed to trigger workflow: " + msg);
  }
}

document.getElementById("runUpdate").addEventListener("click", triggerWorkflow);
