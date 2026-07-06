/* Kong Posh — rename the brand in one place. */
const BRAND_NAME = "Kong Posh";
const CONTACT_EMAIL = "safayashubham@gmail.com"; // TODO: swap for brand mailbox

document.querySelectorAll("[data-brand]").forEach((el) => {
  el.textContent = BRAND_NAME;
});

const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* Waitlist form: Formspree POST with JS success state and mailto fallback. */
const form = document.getElementById("waitlist-form");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = form.querySelector(".form-status");
    const button = form.querySelector("button[type=submit]");
    status.className = "form-status";
    status.textContent = "Sending…";
    button.disabled = true;
    try {
      const res = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error("submit failed");
      form.querySelectorAll("input").forEach((i) => (i.type === "checkbox" ? (i.checked = false) : (i.value = "")));
      status.classList.add("ok");
      status.textContent = "You are on the list. We will write when the founding harvest opens.";
    } catch (err) {
      status.classList.add("err");
      status.innerHTML =
        'We could not reach the form service. Please email us directly at <a href="mailto:' +
        CONTACT_EMAIL +
        "?subject=" +
        encodeURIComponent(BRAND_NAME + " waitlist") +
        '">' +
        CONTACT_EMAIL +
        "</a>.";
    } finally {
      button.disabled = false;
    }
  });
}

/* verify.html — batch certificate renderer */
const verifyRoot = document.getElementById("verify-root");
if (verifyRoot) {
  const params = new URLSearchParams(window.location.search);
  const batchId = (params.get("batch") || "").trim().toUpperCase();

  const stigmaMark =
    '<svg viewBox="0 0 60 32" width="54" height="29" role="img" aria-label="Kong Posh three-stigma seal">' +
    '<path d="M30 30 V14 M30 15 C26 11 24 8 24 4 M30 15 C30 11 30 8 30 4 M30 15 C34 11 36 8 36 4" stroke="#a61c2b" stroke-width="1.8" fill="none" stroke-linecap="round"/>' +
    '<circle cx="24" cy="4" r="1.6" fill="#d99a2b"/><circle cx="30" cy="3.4" r="1.6" fill="#d99a2b"/><circle cx="36" cy="4" r="1.6" fill="#d99a2b"/></svg>';

  const renderNotFound = (id) => {
    verifyRoot.innerHTML =
      '<div class="not-found"><h2>Batch not found</h2>' +
      "<p>" +
      (id
        ? "No record matches <strong>" + id.replace(/[<>&]/g, "") + "</strong>."
        : "No batch number was provided.") +
      " Check the number printed on the base of your tin.</p>" +
      '<p>If the number is correct and still not found, contact us at <a href="mailto:' +
      CONTACT_EMAIL +
      "?subject=" +
      encodeURIComponent(BRAND_NAME + " batch verification") +
      '">' +
      CONTACT_EMAIL +
      "</a> — we take this seriously.</p></div>";
  };

  fetch("batches.json")
    .then((r) => r.json())
    .then((data) => {
      const batch = (data.batches || []).find((b) => b.id === batchId);
      if (!batch) return renderNotFound(batchId);
      verifyRoot.innerHTML =
        '<article class="certificate" aria-label="Batch verification certificate">' +
        '<div class="cert-head">' +
        '<p class="cert-kicker">Certificate of provenance</p>' +
        "<h2>Batch " + batch.id + "</h2>" +
        '<span class="cert-grade">' + batch.grade + "</span>" +
        "</div>" +
        '<ul class="cert-rows">' +
        '<li><span class="k">Harvest window</span><span class="v">' + batch.harvestWindow + "</span></li>" +
        '<li><span class="k">Village of origin</span><span class="v">' + batch.village + "</span></li>" +
        '<li><span class="k">Colouring strength (crocin)</span><span class="v">' + batch.crocin + "</span></li>" +
        '<li><span class="k">Laboratory test date</span><span class="v">' + batch.labTestDate + "</span></li>" +
        '<li><span class="k">Tested by</span><span class="v">' + batch.lab + "</span></li>" +
        "</ul>" +
        '<p class="cert-foot">This record is published by ' + BRAND_NAME + " and matches the batch number sealed on the tin.</p>" +
        '<div class="cert-mark">' + stigmaMark + "</div>" +
        "</article>";
    })
    .catch(() => renderNotFound(batchId));
}
