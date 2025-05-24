// == Text Enhancer Content Script with Undo ==

// 1) Static settings
const ENDPOINT = "http://127.0.0.1:8000/generate";
let CONTEXT  = "The user is talking with Tunisian language mixed with English or French words. The subject is the user is a psychic and can use words from the psychics dictionary";
let RULES    = "Your response must have the same meaning as the user input, no enrichment, the output must be in ENGLISH only";
let TASK     = "Smart translate the user input to English";
let last_user_input_request = ""; // New variable to store last input

console.log("✅ Text Enhancer content script loaded");

// 2) Create all icons
const icon = document.createElement("img");
icon.src = chrome.runtime.getURL("icon.png");
icon.className = "enhancer-icon";
Object.assign(icon.style, {
  position: "absolute",
  width: "16px",
  height: "16px",
  cursor: "pointer",
  display: "none",
  zIndex: 2147483647
});
document.body.appendChild(icon);

const undoIcon = document.createElement("img");
undoIcon.src = chrome.runtime.getURL("re-icon.png");  
undoIcon.className = "enhancer-icon undo-icon";
Object.assign(undoIcon.style, {
  position: "absolute",
  width: "16px",
  height: "16px",
  cursor: "pointer",
  display: "none",
  zIndex: 2147483647
});
document.body.appendChild(undoIcon);

const settingsIcon = document.createElement("img");
settingsIcon.src = chrome.runtime.getURL("settings-icon.png");
settingsIcon.className = "enhancer-icon settings-icon";
Object.assign(settingsIcon.style, {
  position: "absolute",
  width: "16px",
  height: "16px",
  cursor: "pointer",
  display: "none",
  zIndex: 2147483647
});
document.body.appendChild(settingsIcon);

// 3) Create settings popup
const popup = document.createElement("div");
Object.assign(popup.style, {
  position: "fixed",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  backgroundColor: "white",
  border: "1px solid #ccc",
  padding: "10px",
  width: "320px",
  boxShadow: "0 0 10px rgba(0,0,0,0.2)",
  display: "none",
  zIndex: 2147483648,
  fontSize: "12px",
  fontFamily: "Arial, sans-serif"
});
popup.innerHTML = `
  <label style="font-weight:bold;">CONTEXT:</label><br>
  <textarea id="contextInput" style="width: 100%; height: 60px; resize: vertical;">${CONTEXT}</textarea><br><br>
  
  <label style="font-weight:bold;">RULES:</label><br>
  <textarea id="rulesInput" style="width: 100%; height: 60px; resize: vertical;">${RULES}</textarea><br><br>
  
  <label style="font-weight:bold;">TASK:</label><br>
  <textarea id="taskInput" style="width: 100%; height: 40px; resize: vertical;">${TASK}</textarea><br><br>
  
  <button id="saveBtn" style="padding: 5px 10px;">Save</button>
  <button id="cancelBtn" style="padding: 5px 10px; margin-left:10px;">Cancel</button>
`;
document.body.appendChild(popup);

// 4) Helper functions
function isEditable(el) {
  return el && (
    (el.tagName === "INPUT" && (el.type === "text" || el.type === "search")) ||
    el.tagName === "TEXTAREA" ||
    el.isContentEditable
  );
}

function positionIcons(el) {
  if (!el) return;
  
  const r = el.getBoundingClientRect();
  const baseTop = r.top + window.scrollY;
  const baseLeft = r.left + window.scrollX + r.width + 5; // 5px right of element

  // Stack icons vertically with 6px spacing
  icon.style.top = `${baseTop + 2}px`;
  icon.style.left = `${baseLeft}px`;
  icon.style.display = "block";

  settingsIcon.style.top = `${baseTop + 22}px`;  // 16px height + 6px spacing
  settingsIcon.style.left = `${baseLeft}px`;
  settingsIcon.style.display = "block";

  // Always show undo icon
  undoIcon.style.top = `${baseTop + 44}px`;  // 16px height * 2 + 6px*2 spacing
  undoIcon.style.left = `${baseLeft}px`;
  undoIcon.style.display = "block";
}

// 5) Event listeners
let activeElement = null;

document.addEventListener("focusin", (e) => {
  const el = e.target;
  if (!isEditable(el)) {
    icon.style.display = "none";
    settingsIcon.style.display = "none";
    undoIcon.style.display = "none";
    return;
  }

  activeElement = el;
  positionIcons(el);
});

// Keep icons positioned correctly during scrolling/resizing
document.addEventListener("scroll", () => positionIcons(activeElement), { passive: true });
window.addEventListener("resize", () => positionIcons(activeElement));

// 6) Main icon click handler
icon.addEventListener("click", async () => {
  if (!activeElement) return;

  let text;
  try {
    text = activeElement.isContentEditable ? activeElement.innerText : activeElement.value;
    last_user_input_request = text; // Store the original text
  } catch (err) {
    console.error("Error getting text:", err);
    return;
  }

  try {
    console.log("Sending text to server:", text);
    const payload = { text, context: CONTEXT, rules: RULES, task: TASK };

    const resp = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) throw new Error(resp.statusText);
    const json = await resp.json();

    if (typeof json.response !== "string") {
      throw new Error("Invalid response format");
    }

    if (activeElement.isContentEditable) {
      activeElement.innerText = json.response;
    } else {
      activeElement.value = json.response;
    }
  } catch (err) {
    console.error("Enhancer error:", err);
  }
});

// 7) Undo icon click handler - always visible and uses last_user_input_request
undoIcon.addEventListener("click", () => {
  if (!activeElement || !last_user_input_request) return;

  if (activeElement.isContentEditable) {
    activeElement.innerText = last_user_input_request;
  } else {
    activeElement.value = last_user_input_request;
  }
  
  // Reset the stored value after undo
  last_user_input_request = "";
});

// 8) Settings icon and popup handlers
settingsIcon.addEventListener("click", () => {
  popup.querySelector("#contextInput").value = CONTEXT;
  popup.querySelector("#rulesInput").value = RULES;
  popup.querySelector("#taskInput").value = TASK;
  popup.style.display = "block";
});

popup.querySelector("#saveBtn").addEventListener("click", () => {
  CONTEXT = popup.querySelector("#contextInput").value.trim();
  RULES = popup.querySelector("#rulesInput").value.trim();
  TASK = popup.querySelector("#taskInput").value.trim();
  popup.style.display = "none";
});

popup.querySelector("#cancelBtn").addEventListener("click", () => {
  popup.style.display = "none";
});