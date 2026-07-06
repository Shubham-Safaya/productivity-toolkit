/* Sundays with Safaya — rename the brand in one place. */
const BRAND_NAME = "Sundays with Safaya";
const CONTACT_EMAIL = "safayashubham@gmail.com";

document.querySelectorAll("[data-brand]").forEach((el) => {
  el.textContent = BRAND_NAME;
});

const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* Signature: the Sunday cadence device — compute the date of the next Sunday. */
const nextSundayEl = document.getElementById("next-sunday");
if (nextSundayEl) {
  const now = new Date();
  const daysUntilSunday = (7 - now.getDay()) % 7 || 7;
  const next = new Date(now);
  next.setDate(now.getDate() + daysUntilSunday);
  const formatted = next.toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
  nextSundayEl.textContent = "Next note: " + formatted;
}

/* Signup form: Formspree POST with JS success state and mailto fallback. */
const form = document.getElementById("signup-form");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = form.querySelector(".form-status");
    const button = form.querySelector("button[type=submit]");
    status.className = "form-status";
    status.textContent = "Signing you up…";
    button.disabled = true;
    try {
      const res = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error("submit failed");
      form.querySelectorAll("input").forEach((i) => (i.value = ""));
      status.classList.add("ok");
      status.textContent = "Done. The next note lands on Sunday.";
    } catch (err) {
      status.classList.add("err");
      status.innerHTML =
        'The form service did not respond. Email <a href="mailto:' +
        CONTACT_EMAIL +
        "?subject=" +
        encodeURIComponent("Sunday note signup") +
        '">' +
        CONTACT_EMAIL +
        "</a> and I will add you by hand.";
    } finally {
      button.disabled = false;
    }
  });
}
