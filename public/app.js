const form = document.querySelector("#parser-form");
const providerSelect = document.querySelector("#provider");
const fileInput = document.querySelector("#file");
const fileName = document.querySelector("#file-name");
const submitButton = document.querySelector("#submit");
const statusText = document.querySelector("#status");
const optionInputs = document.querySelectorAll(".option-card input");

if (window.self !== window.top || new URLSearchParams(window.location.search).get("embedded") === "true") {
  document.body.classList.add("embedded");
}

const providerHeaders = {
  bondora: ["TransferDate", "Description", "LoanNumber", "Amount", "Currency"],
  bondora_go_grow: ["TransferDate", "Description", "LoanNumber", "Amount", "Currency"],
  debitumnetwork: ["Date", "Transaction ID", "Transaction Type", "Turnover", "Asset ID"],
  estateguru_de_legacy: ["Zahlungsdatum", "Projektname", "UniqueId", "Cashflow-Typ", "Betrag", "Währung"],
  estateguru_de: ["Zahlungsdatum", "Projektname", "ID", "Cashflow-Typ", "Betrag", "Währung"],
  estateguru_en: ["Payment Date", "Loan Code", "ID", "Cash Flow Type", "Amount", "Currency"],
  lande: ["Date", "Loan ID", "Transaction ID", "Type", "Amount"],
  mintos_en: ["Date", "Details", "Transaction ID:", "Turnover", "Currency"],
  mintos_de: ["Datum", "Details", "Transaktions-Nr.:", "Umsatz", "Währung"],
  robocash: ["Date and time", "Credit part ID", "Transaction ID", "Operation", "Amount"],
  swaper: ["Booking date", "Loan id", "Loan number", "Transaction type", "Amount"],
  viainvest: ["Value date", "Loan ID", "Transaction type", "Credit (€)"],
};

const providerLabels = {
  bondora: "Bondora",
  bondora_go_grow: "Bondora Go & Grow",
  debitumnetwork: "Debitum Network",
  estateguru_de: "Estateguru DE",
  estateguru_de_legacy: "Estateguru DE Legacy",
  estateguru_en: "Estateguru EN",
  lande: "Lande",
  mintos_de: "Mintos DE",
  mintos_en: "Mintos EN",
  robocash: "Robocash",
  swaper: "Swaper",
  viainvest: "Viainvest",
};

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) {
    providerSelect.value = "auto";
    fileName.textContent = "No file selected";
    setStatus("");
    return;
  }

  fileName.textContent = file.name;

  try {
    const headerLine = await readHeaderLine(file);
    const detectedProvider = detectProvider(parseCsvLine(headerLine));
    if (detectedProvider) {
      providerSelect.value = detectedProvider;
      setStatus(`Detected the format for ${formatProviderName(detectedProvider)}. You can change it manually.`);
    } else {
      providerSelect.value = "auto";
      setStatus("Could not identify this CSV format. Choose a provider manually.", true);
    }
  } catch (error) {
    providerSelect.value = "auto";
    setStatus(error.message || "Could not read the CSV header.", true);
  }
});

optionInputs.forEach((input) => {
  input.addEventListener("change", updateOptionSelection);
});
updateOptionSelection();

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const file = formData.get("file");

  if (!file || file.size === 0) {
    setStatus("Choose a CSV file first.", true);
    return;
  }

  submitButton.disabled = true;
  setStatus("Converting...");

  try {
    const response = await fetch("/parse", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(await readError(response));
    }

    const blob = await response.blob();
    const filename = getDownloadFilename(response) || "portfolio_performance.csv";
    downloadBlob(blob, filename);
    setStatus(`Downloaded ${filename}`);
  } catch (error) {
    setStatus(error.message || "Conversion failed.", true);
  } finally {
    submitButton.disabled = false;
  }
});

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.classList.toggle("visible", Boolean(message));
  statusText.classList.toggle("error", isError);
}

function updateOptionSelection() {
  optionInputs.forEach((input) => {
    input.closest(".option-card").classList.toggle("selected", input.checked);
  });
}

async function readError(response) {
  const contentType = response.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) {
    const body = await response.json();
    return body.error || "Conversion failed.";
  }
  return (await response.text()) || "Conversion failed.";
}

async function readHeaderLine(file) {
  const text = await file.slice(0, 4096).text();
  const line = text.replace(/^\uFEFF/, "").split(/\r?\n/).find((item) => item.trim());
  if (!line) {
    throw new Error("The CSV file is empty.");
  }
  return line;
}

function parseCsvLine(line) {
  const values = [];
  let value = "";
  let inQuotes = false;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];

    if (char === '"' && inQuotes && next === '"') {
      value += '"';
      index += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      values.push(value.trim());
      value = "";
    } else {
      value += char;
    }
  }

  values.push(value.trim());
  return values;
}

function detectProvider(headers) {
  const headerSet = new Set(headers);
  return Object.entries(providerHeaders).find(([, requiredHeaders]) =>
    requiredHeaders.every((header) => headerSet.has(header)),
  )?.[0];
}

function formatProviderName(provider) {
  return providerLabels[provider] || provider;
}

function getDownloadFilename(response) {
  const disposition = response.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="([^"]+)"/);
  return match ? match[1] : "";
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
