/* ThreadPass — rename the brand in one place. */
const BRAND_NAME = "ThreadPass";
const CONTACT_EMAIL = "safayashubham@gmail.com"; // TODO: swap for brand mailbox

document.querySelectorAll("[data-brand]").forEach((el) => {
  el.textContent = BRAND_NAME;
});

const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* Signature element: one continuous thread stitched down the page,
   passing through a node beside every [data-node] section. */
(function drawThread() {
  const svg = document.getElementById("thread-svg");
  const path = document.getElementById("thread-path");
  if (!svg || !path) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function build() {
    const docH = document.documentElement.scrollHeight;
    const railW = document.querySelector(".thread-rail").offsetWidth;
    const x = Math.max(railW * 0.55, 12);
    svg.setAttribute("viewBox", "0 0 " + railW + " " + docH);
    svg.style.height = docH + "px";

    const nodes = Array.from(document.querySelectorAll("[data-node]")).map((s) => {
      const r = s.getBoundingClientRect();
      return r.top + window.scrollY + 24;
    });

    let d = "M " + x + " 0";
    nodes.forEach((y) => {
      // a small stitch loop at each section
      d += " L " + x + " " + (y - 14);
      d += " C " + (x + 10) + " " + (y - 8) + " " + (x + 10) + " " + (y + 8) + " " + x + " " + (y + 14);
    });
    d += " L " + x + " " + docH;
    path.setAttribute("d", d);

    const len = path.getTotalLength();
    if (reduceMotion) {
      path.style.strokeDasharray = "none";
      path.style.strokeDashoffset = "0";
      return len;
    }
    path.style.strokeDasharray = len + " " + len;
    return len;
  }

  let length = build();

  function onScroll() {
    if (reduceMotion) return;
    const scrolled = window.scrollY + window.innerHeight;
    const total = document.documentElement.scrollHeight;
    const progress = Math.min(scrolled / total, 1);
    path.style.strokeDashoffset = String(length * (1 - progress));
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", () => { length = build(); onScroll(); });
  onScroll();
})();

/* Checklist live score */
(function checklistScore() {
  const boxes = document.querySelectorAll(".checklist input[type=checkbox]");
  const score = document.getElementById("checklist-score");
  if (!boxes.length || !score) return;
  const messages = [
    "0 of 8 — you are not alone, but the clock is running.",
    " of 8 — a start. The gaps are where detentions happen.",
    " of 8 — better than most. The last items are the hard ones.",
    " of 8 — you are close. A review would confirm it.",
    "8 of 8 — strong. A review would pressure-test the evidence behind each yes.",
  ];
  function update() {
    const n = Array.from(boxes).filter((b) => b.checked).length;
    if (n === 0) score.textContent = messages[0];
    else if (n <= 3) score.textContent = n + messages[1];
    else if (n <= 5) score.textContent = n + messages[2];
    else if (n <= 7) score.textContent = n + messages[3];
    else score.textContent = messages[4];
  }
  boxes.forEach((b) => b.addEventListener("change", update));
})();

/* Review form: Formspree POST with JS success state and mailto fallback. */
const form = document.getElementById("review-form");
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
      form.querySelectorAll("input").forEach((i) => (i.value = ""));
      status.classList.add("ok");
      status.textContent = "Received. We will reach out within two working days to schedule the review.";
    } catch (err) {
      status.classList.add("err");
      status.innerHTML =
        'We could not reach the form service. Please email us directly at <a href="mailto:' +
        CONTACT_EMAIL +
        "?subject=" +
        encodeURIComponent(BRAND_NAME + " readiness review") +
        '">' +
        CONTACT_EMAIL +
        "</a>.";
    } finally {
      button.disabled = false;
    }
  });
}
