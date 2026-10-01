const registerView = document.querySelector("#register-view");
const loginView = document.querySelector("#login-view");
const patientView = document.querySelector("#patient-view");
const successView = document.querySelector("#success-view");
const profileForm = document.querySelector("#profile-form");
const loginForm = document.querySelector("#login-form");
const patientForm = document.querySelector("#patient-form");
const licenseField = document.querySelector("#license-field");

function setMode(mode) {
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.mode === mode);
  });
  registerView.classList.toggle("hidden", mode !== "register");
  loginView.classList.toggle("hidden", mode !== "login");
  patientView.classList.toggle("hidden", mode !== "patient");
  successView.classList.add("hidden");
}

document.querySelectorAll(".mode-tab").forEach((tab) => {
  tab.addEventListener("click", () => setMode(tab.dataset.mode));
});

document.querySelectorAll('input[name="role"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    document.querySelectorAll(".role-option").forEach((option) => {
      option.classList.toggle("selected", option.contains(radio) && radio.checked);
    });
    const isDoctor = radio.value === "doctor" && radio.checked;
    licenseField.classList.toggle("hidden", !isDoctor);
    licenseField.querySelector("input").required = isDoctor;
  });
});

document.querySelectorAll("[data-password-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = button.parentElement.querySelector("input");
    const showing = input.type === "text";
    input.type = showing ? "password" : "text";
    button.setAttribute("aria-label", showing ? "Show password" : "Hide password");
    button.innerHTML = `<i data-lucide="${showing ? "eye" : "eye-off"}"></i>`;
    window.lucide.createIcons();
  });
});

function payloadFrom(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function setSubmitting(form, submitting) {
  const button = form.querySelector('button[type="submit"]');
  button.disabled = submitting;
  button.querySelector("span").textContent = submitting ? "Please wait..." : button.dataset.label;
}

function apiError(data) {
  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => item.msg.replace("Value error, ", "")).join(". ");
  }
  return data.detail || "Unable to complete the request";
}

profileForm.querySelector('button[type="submit"]').dataset.label = "Create profile";
loginForm.querySelector('button[type="submit"]').dataset.label = "Sign in";
patientForm.querySelector('button[type="submit"]').dataset.label = "Save patient";

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#profile-message");
  message.textContent = "";
  if (!profileForm.reportValidity()) return;

  const payload = payloadFrom(profileForm);
  payload.years_of_experience = Number(payload.years_of_experience);
  if (payload.role !== "doctor") payload.license_number = null;

  setSubmitting(profileForm, true);
  try {
    const response = await fetch("/api/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(apiError(data));
    showSuccess(data);
  } catch (error) {
    message.textContent = error.message;
  } finally {
    setSubmitting(profileForm, false);
  }
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#login-message");
  message.textContent = "";
  if (!loginForm.reportValidity()) return;

  setSubmitting(loginForm, true);
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payloadFrom(loginForm)),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(apiError(data));
    sessionStorage.setItem("hmi_access_token", data.access_token);
    showSuccess(data.profile, true);
  } catch (error) {
    message.textContent = error.message;
  } finally {
    setSubmitting(loginForm, false);
  }
});

patientForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#patient-message");
  message.textContent = "";
  if (!patientForm.reportValidity()) return;

  const payload = payloadFrom(patientForm);
  payload.age = Number(payload.age);
  if (!payload.appointment_reason) payload.appointment_reason = null;

  setSubmitting(patientForm, true);
  try {
    const response = await fetch("/api/patients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(apiError(data));
    patientForm.reset();
    showPatientSuccess(data);
  } catch (error) {
    message.textContent = error.message;
  } finally {
    setSubmitting(patientForm, false);
  }
});

function showSuccess(profile, signedIn = false) {
  registerView.classList.add("hidden");
  loginView.classList.add("hidden");
  successView.classList.remove("hidden");
  document.querySelector("#success-title").textContent = signedIn
    ? `Welcome back, ${profile.full_name}`
    : `Welcome, ${profile.full_name}`;
  const summary = document.querySelector("#profile-summary");
  summary.replaceChildren();
  const details = [
    ["Role", profile.role === "doctor" ? "Doctor" : "Receptionist"],
    ["Email", profile.email],
    ["Profession", profile.profession],
    ["Expertise", profile.area_of_expertise],
  ];
  details.forEach(([label, value]) => {
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = label;
    description.textContent = value;
    summary.append(term, description);
  });
  document.querySelector("#continue-button").classList.toggle("hidden", signedIn);
}

function showPatientSuccess(patient) {
  registerView.classList.add("hidden");
  loginView.classList.add("hidden");
  patientView.classList.add("hidden");
  successView.classList.remove("hidden");
  document.querySelector("#success-title").textContent = `Patient saved: ${patient.full_name}`;
  const summary = document.querySelector("#profile-summary");
  summary.replaceChildren();
  const details = [
    ["Patient ID", patient.id],
    ["Age", patient.age],
    ["Contact", patient.contact_number],
    ["Address", patient.address],
    ["Appointment reason", patient.appointment_reason || "Not specified"],
  ];
  details.forEach(([label, value]) => {
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = label;
    description.textContent = value;
    summary.append(term, description);
  });
  document.querySelector("#continue-button").classList.add("hidden");
}

document.querySelector("#continue-button").addEventListener("click", () => {
  loginForm.elements.email.value = profileForm.elements.email.value;
  setMode("login");
});

window.lucide.createIcons();