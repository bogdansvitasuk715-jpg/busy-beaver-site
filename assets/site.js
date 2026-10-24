  /* ===== Placeholders until confirmed ===== */
  const CONFIG = {
    phoneDisplay: "(859) 800-5955",
    phoneTel: "+18598005955",
    email: "busybeaverky@gmail.com",
    liveForm: true,          // Netlify Forms: sends requests to the account email
    // Popup for first-time visitors. enabled: false turns it off
    offer: {
      enabled: true,
      tag: "New customer special",
      amount: "$50 OFF",
      line: "On your first handyman job",
      terms: "For new customers in our service area. Good on repairs, installs and upkeep. We add it to your estimate automatically.",
      summary: "$50 off first job (new customer)",
      delaySeconds: 6
    }
  };

  document.querySelectorAll("[data-phone]").forEach(el => el.textContent = CONFIG.phoneDisplay);
  document.querySelectorAll("[data-email-label]").forEach(el => el.textContent = CONFIG.email);
  document.querySelectorAll("[data-tel]").forEach(a => {
    if (CONFIG.phoneTel) a.href = "tel:" + CONFIG.phoneTel;
    else a.addEventListener("click", e => { e.preventDefault(); toast("Phone number coming soon."); });
  });
  document.querySelectorAll("[data-email]").forEach(a => {
    if (CONFIG.email.includes("@")) a.href = "mailto:" + CONFIG.email;
    else a.addEventListener("click", e => { e.preventDefault(); toast("Email address coming soon."); });
  });
  document.getElementById("year").textContent = new Date().getFullYear();

  // Toast for links to pages that aren't built yet
  const toastEl = document.getElementById("toast");
  let toastTimer;
  function toast(msg) {
    toastEl.textContent = msg; toastEl.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => toastEl.hidden = true, 3000);
  }
  document.querySelectorAll("[data-soon]").forEach(a => a.addEventListener("click", e => { e.preventDefault(); toast("This page is coming soon."); }));

  // Mobile menu
  const menuBtn = document.querySelector(".menu-btn");
  const mobileNav = document.getElementById("mobile-nav");
  const setMenu = open => { mobileNav.hidden = !open; menuBtn.setAttribute("aria-expanded", String(open)); menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu"); };
  menuBtn.addEventListener("click", () => setMenu(mobileNav.hidden));
  mobileNav.addEventListener("click", e => { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !mobileNav.hidden) { setMenu(false); menuBtn.focus(); } });

  // New-customer offer popup: once per visitor, add #offer to the address to see it again
  const offer = document.getElementById("offer");
  const offerChip = document.getElementById("offer-chip");
  const store = { get(k) { try { return localStorage.getItem(k); } catch { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch {} } };
  const goQuote = () => {
    if (!document.getElementById("quote")) { location.href = (document.querySelector(".logo")?.getAttribute("href") || "index.html") + "#quote"; return; }
    document.getElementById("quote").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    setTimeout(() => document.getElementById("q-name").focus({ preventScroll: true }), 550);
  };
  const applyOffer = () => { const f = document.getElementById("q-offer"); if (f) { f.value = CONFIG.offer.summary; offerChip.hidden = false; } };
  if (!CONFIG.offer.enabled) document.querySelectorAll("[data-offer-only]").forEach(el => el.hidden = true);
  if (CONFIG.offer.enabled) {
    document.querySelectorAll("[data-offer]").forEach(el => el.textContent = CONFIG.offer[el.dataset.offer]);
    document.querySelectorAll("[data-open-offer]").forEach(el => el.addEventListener("click", e => { e.preventDefault(); offer.showModal(); }));
    const openOffer = () => { if (!document.querySelector("dialog[open]") && helper.hidden) offer.showModal(); };
    if (location.hash === "#offer") setTimeout(openOffer, 400);
    else if (!store.get("bb-offer-seen")) setTimeout(openOffer, CONFIG.offer.delaySeconds * 1000);
    offer.addEventListener("close", () => store.set("bb-offer-seen", "1"));
    offer.addEventListener("click", e => { if (e.target === offer || e.target.closest("[data-offer-close]")) offer.close(); });
    offer.querySelector("[data-offer-claim]").addEventListener("click", () => { offer.close(); applyOffer(); goQuote(); });
    document.getElementById("offer-remove")?.addEventListener("click", () => { document.getElementById("q-offer").value = ""; offerChip.hidden = true; });
  }

  // Ask Busy Beaver: answers common questions from what's on this page
  const helperBtn = document.getElementById("helper-btn");
  const helper = document.getElementById("helper-panel");
  const log = document.getElementById("helper-log");
  const say = (text, who = "bot", actions = []) => {
    const m = document.createElement("div"); m.className = "msg " + who; m.textContent = text; log.append(m);
    if (actions.length) { const row = document.createElement("div"); row.className = "msg-actions"; actions.forEach(a => row.append(a)); log.append(row); }
    log.scrollTop = log.scrollHeight;
  };
  const act = (label, fn, solid) => { const b = document.createElement("button"); b.type = "button"; b.textContent = label; if (solid) b.className = "solid"; b.addEventListener("click", fn); return b; };
  const toQuote = () => { setHelper(false); goQuote(); };
  const answers = {
    services: () => say("General repairs, drywall, painting, TV mounting, furniture assembly, doors and locks, gutter cleaning, lights and fixtures, and junk removal. Send the whole list and we'll knock out several jobs in one visit.", "bot", [act("Get a free estimate", toQuote, true)]),
    area: () => say("We're based in Lexington and work in Nicholasville, Georgetown, Versailles, Winchester, Richmond and Paris. Close by but not on the list? Ask us, we'll check your address."),
    price: () => say("Every job is different, so we price it after a quick look. Send a few photos and you'll get a clear price before any work starts. The estimate is free.", "bot", [act("Send photos for a quote", toQuote, true)]),
    offer: () => CONFIG.offer.enabled ? say(`New customers get ${CONFIG.offer.amount.toLowerCase()} their first handyman job.`, "bot", [act("Claim offer", () => { setHelper(false); applyOffer(); goQuote(); }, true)]) : say("Ask about current specials when you request your estimate."),
    when: () => say("We reply to every request within 1 business day, then offer you the next open time that fits your schedule."),
    insured: () => say("Yes, Busy Beaver Handyman is insured. We're happy to send proof of coverage before the job."),
    book: () => { say("On it! Taking you to the quote form."); setTimeout(toQuote, 700); },
    human: () => say(CONFIG.phoneTel ? `Call or text us at ${CONFIG.phoneDisplay}.` : "Our phone line is being set up. For now, the quote form is the fastest way to reach us.", "bot", [act("Open the quote form", toQuote, true)])
  };
  const keywords = [
    ["unknown", /roof|plumb|electric|wiring|hvac|furnace|pest|concrete|foundation|pool/i],
    ["offer", /deal|discount|offer|coupon|special|promo|%|percent|off\b/i],
    ["price", /price|cost|how much|quote|estimate|charge|rate|\$/i],
    ["insured", /insur|licen|bond|guarant/i],
    ["when", /soon|when|today|tomorrow|week|available|schedule|time/i],
    ["area", /where|area|come to|town|city|lexington|nicholasville|georgetown|versailles|winchester|richmond|paris|address|zip/i],
    ["human", /call|phone|text|email|person|human|talk|contact|number/i],
    ["services", /tv|mount|drywall|paint|door|lock|gutter|furniture|assembl|light|fixture|fan|faucet|junk|haul|repair|fix|install|shelf|do you/i]
  ];
  const ask = (q, label) => {
    say(label, "me");
    setTimeout(() => (answers[q] || (() => say("Good question, and I don't want to guess. Send it with the quote form and a real person will answer within 1 business day.", "bot", [act("Open the quote form", toQuote, true)])))(), 350);
  };
  const setHelper = open => {
    helper.hidden = !open; helperBtn.setAttribute("aria-expanded", String(open));
    if (open && !log.children.length) say("Hi, I'm Busy Beaver! Ask me about our services, prices, towns or the new customer deal.");
    if (open) document.getElementById("helper-input").focus(); else helperBtn.focus();
  };
  helperBtn.addEventListener("click", () => setHelper(helper.hidden));
  document.querySelectorAll("[data-open-helper]").forEach(a => a.addEventListener("click", e => { e.preventDefault(); setHelper(true); }));
  document.getElementById("helper-close").addEventListener("click", () => setHelper(false));
  document.getElementById("helper-chips").addEventListener("click", e => { const b = e.target.closest("[data-q]"); if (b) ask(b.dataset.q, b.textContent); });
  document.getElementById("helper-form").addEventListener("submit", e => {
    e.preventDefault();
    const input = document.getElementById("helper-input"); const text = input.value.trim(); if (!text) return;
    input.value = ""; const hit = keywords.find(([, re]) => re.test(text)); ask(hit ? hit[0] : null, text);
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !helper.hidden) setHelper(false); });

  // Scrolling reviews: pause button (hover and keyboard focus pause too, in CSS)
  const reviewsToggle = document.querySelector(".marquee-toggle");
  if (reviewsToggle) {
    reviewsToggle.addEventListener("click", () => {
      const paused = reviewsToggle.getAttribute("aria-pressed") !== "true";
      reviewsToggle.setAttribute("aria-pressed", paused);
      reviewsToggle.textContent = paused ? "Play scrolling reviews" : "Pause scrolling reviews";
      document.getElementById("reviews").classList.toggle("is-paused", paused);
    });
  }

  // Before/after viewer with click-to-zoom (only on pages with a gallery)
  const shots = [...document.querySelectorAll(".shot")];
  const lb = document.getElementById("lightbox");
  if (shots.length && lb) {
    const lbImg = lb.querySelector(".lb-stage img");
    const lbCap = document.getElementById("lightbox-caption");
    const lbCount = document.getElementById("lb-count");
    let current = 0;
    const unzoom = () => { lbImg.classList.remove("zoomed"); lbImg.style.transformOrigin = "50% 50%"; };
    const show = i => {
      current = (i + shots.length) % shots.length;
      const s = shots[current];
      unzoom(); lbImg.style.animation = "none"; void lbImg.offsetWidth; lbImg.style.animation = "";
      lbImg.src = s.dataset.full; lbImg.alt = s.querySelector("img").alt;
      lbCap.textContent = s.dataset.title;
      lbCount.textContent = `${current + 1} of ${shots.length} · Tap the photo to zoom`;
    };
    const setOrigin = e => {
      const r = lbImg.getBoundingClientRect();
      lbImg.style.transformOrigin = `${Math.min(100, Math.max(0, (e.clientX - r.left) / r.width * 100))}% ${Math.min(100, Math.max(0, (e.clientY - r.top) / r.height * 100))}%`;
    };
    lbImg.addEventListener("click", e => { e.stopPropagation(); if (lbImg.classList.contains("zoomed")) { unzoom(); return; } setOrigin(e); lbImg.classList.add("zoomed"); });
    lbImg.addEventListener("pointermove", e => { if (lbImg.classList.contains("zoomed") && e.pointerType === "mouse") setOrigin(e); });
    shots.forEach((s, i) => s.addEventListener("click", () => { show(i); lb.showModal(); }));
    lb.addEventListener("click", e => {
      const a = e.target.closest("[data-lb]")?.dataset.lb;
      if (a === "prev") show(current - 1); else if (a === "next") show(current + 1);
      else if (a === "close" || e.target === lb || e.target.classList.contains("lb-stage")) lb.close();
    });
    lb.addEventListener("keydown", e => { if (e.key === "ArrowLeft") show(current - 1); if (e.key === "ArrowRight") show(current + 1); });
    lb.addEventListener("close", () => { unzoom(); shots[current].focus(); });
  }

  // ZIP check: tells visitors if we serve them, then opens the quote form with the town filled in
  const zipForm = document.getElementById("zip-form");
  if (zipForm) {
    const zipMap = {};
    zipForm.dataset.zips.split(";").forEach(row => { const [town, list] = row.split(":"); list.split(",").forEach(z => zipMap[z] = town); });
    const result = document.getElementById("zip-result");
    const input = document.getElementById("zip-input");
    input.addEventListener("input", () => { input.value = input.value.replace(/\D/g, "").slice(0, 5); });
    const toForm = (town, zip) => {
      const sel = document.getElementById("q-town");
      if (town) sel.value = town; else sel.value = "Somewhere else nearby";
      document.getElementById("q-zip").value = zip;
      setTimeout(goQuote, 900);
    };
    zipForm.addEventListener("submit", e => {
      e.preventDefault();
      const zip = input.value.trim();
      result.className = "zip-result";
      if (!/^\d{5}$/.test(zip)) { result.classList.add("bad"); result.textContent = "Enter a 5-digit ZIP code, like 40502."; input.focus(); return; }
      const town = zipMap[zip];
      if (town) { result.classList.add("ok"); result.textContent = `Good news! We work in ${town}. Taking you to the quote form…`; toForm(town, zip); }
      else if (zip.startsWith("40")) { result.classList.add("maybe"); result.textContent = "You're close to our area. Send your request and we'll confirm your address."; toForm(null, zip); }
      else { result.classList.add("bad"); result.textContent = "That ZIP looks outside Central Kentucky. We work around Lexington, KY."; }
    });
  }

  // Quote form
  const form = document.getElementById("quote-form");
  if (form) {
  const fileInput = document.getElementById("q-photos");
  const thumbs = document.getElementById("thumbs");
  const drop = document.getElementById("drop");
  const status = document.getElementById("form-status");
  const MAX_FILES = 5, MAX_TOTAL = 8 * 1024 * 1024;   // Netlify Forms limit per request
  let photos = [];
  const photoErr = m => document.getElementById("e-photos").textContent = m;
  const addFiles = list => {
    photoErr("");
    for (const f of list) {
      if (!f.type.startsWith("image/")) { photoErr(`"${f.name}" isn't a photo. Add JPG, PNG or HEIC files.`); continue; }
      if (photos.length >= MAX_FILES) { photoErr("You can add up to 5 photos."); break; }
      if (photos.reduce((t, p) => t + p.size, 0) + f.size > MAX_TOTAL) { photoErr("Photos are over 8 MB in total. Remove one or send smaller photos."); break; }
      photos.push(f);
    }
    render(); fileInput.value = "";
  };
  const render = () => {
    thumbs.querySelectorAll("img").forEach(i => URL.revokeObjectURL(i.src));
    thumbs.innerHTML = "";
    photos.forEach((f, i) => {
      const li = document.createElement("li"), img = document.createElement("img"), rm = document.createElement("button");
      img.src = URL.createObjectURL(f); img.alt = f.name;
      rm.type = "button"; rm.setAttribute("aria-label", "Remove " + f.name); rm.innerHTML = '<svg aria-hidden="true"><use href="#i-x"/></svg>';
      rm.addEventListener("click", () => { photos.splice(i, 1); render(); fileInput.focus(); });
      li.append(img, rm); thumbs.append(li);
    });
  };
  fileInput.addEventListener("change", () => addFiles(fileInput.files));
  ["dragenter", "dragover"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add("drag"); }));
  ["dragleave", "drop"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove("drag"); }));
  drop.addEventListener("drop", e => addFiles(e.dataTransfer.files));

  const rules = {
    name:  v => v.trim() ? "" : "Enter your name.",
    phone: v => v.replace(/\D/g, "").length >= 10 ? "" : "Enter a 10-digit phone number.",
    email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()) ? "" : "Enter an email like name@example.com.",
    job:   v => v.trim().length >= 10 ? "" : "Tell us a little about the job (a sentence is fine)."
  };
  const check = input => {
    const msg = rules[input.name](input.value);
    input.setAttribute("aria-invalid", msg ? "true" : "false");
    document.getElementById(input.getAttribute("aria-describedby").split(" ").pop()).textContent = msg;
    return !msg;
  };
  Object.keys(rules).forEach(n => {
    const el = form.elements[n];
    el.addEventListener("blur", () => { if (el.value) check(el); });
    el.addEventListener("input", () => { if (el.getAttribute("aria-invalid") === "true") check(el); });
  });
  form.addEventListener("submit", async e => {
    e.preventDefault();
    status.className = "form-status"; status.textContent = "";
    const bad = Object.keys(rules).map(n => form.elements[n]).filter(el => !check(el));
    if (bad.length) { bad[0].focus(); return; }
    if (!CONFIG.liveForm) { status.classList.add("bad"); status.textContent = "Preview only: the form starts sending once the site is live."; return; }
    const btn = form.querySelector('[type="submit"]');
    const data = new FormData(form); data.delete("photos"); photos.forEach(f => data.append("photos", f));
    btn.disabled = true; btn.textContent = "Sending…";
    try {
      // Post to the thank-you page: Netlify records the submission and answers with that page
      const res = await fetch("/thank-you", { method: "POST", body: data });
      if (res.status >= 500) throw new Error(res.status);
      form.reset(); photos = []; render(); offerChip.hidden = true;
      status.classList.add("ok"); status.textContent = "Got it! We'll reply within 1 business day.";
      // Thank-you page: Google Ads counts a lead when it loads
      location.assign("/thank-you");
    } catch {
      status.classList.add("bad"); status.textContent = "That didn't send. Check your connection and try again, or call us.";
    } finally { btn.disabled = false; btn.textContent = "Get My Free Estimate"; }
  });

  }