/*
 * Autocomplete form behaviour, implementing FR-01..FR-05.
 *
 *   FR-01  type any value OR click / keyboard-select a suggestion
 *   FR-02  prefix-match filtering (default)
 *   FR-03  match-anywhere filtering (enabled from backend config)
 *   FR-04  Next -> POST /api/response; 200 shows success, otherwise error
 *   FR-05  payload carries text, local-time timestamps, BCP-47 locale, matching suggestions
 */
(function () {
  "use strict";

  var API_BASE = ""; // same origin as the page

  var SUGGESTIONS = [
    "agile methodology",
    "agile methodology process",
    "agile methodology process testing"
  ];

  var input = document.getElementById("input-field");
  var list = document.querySelector(".suggestions");
  var items = Array.prototype.slice.call(list.querySelectorAll("li"));
  var nextBtn = document.getElementById("next-button");
  var errorEl = document.querySelector(".error-message");
  var successEl = document.querySelector(".success-container");

  var config = { filter_mode: "prefix", require_suggestion_selection: false };

  // The suggestion list stays hidden until the user types a matching value; it is
  // re-suppressed on load, on Escape, and after a suggestion is selected.
  var listSuppressed = true;

  // FR-05: timestamp in the user's local time when they *reached* the form.
  var startDate = toLocalISO(new Date());

  // ---- helpers --------------------------------------------------------------
  function pad(n) { return String(n).padStart(2, "0"); }

  function toLocalISO(d) {
    // ISO-8601 keeping the browser's local UTC offset, e.g. 2024-03-15T16:00:00+05:30
    var offset = -d.getTimezoneOffset();      // minutes east of UTC (IST => +330)
    var sign = offset >= 0 ? "+" : "-";
    var abs = Math.abs(offset);
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      "T" + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()) +
      sign + pad(Math.floor(abs / 60)) + ":" + pad(abs % 60);
  }

  function regionFromTimeZone() {
    var tz = "";
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) { /* noop */ }
    var map = { "Asia/Kolkata": "IN", "Asia/Calcutta": "IN" };
    return map[tz] || "IN";
  }

  function resolveLocale() {
    // FR-05: IETF BCP 47 including region. Test env is English + India => en-IN.
    var lang = navigator.language || "en";
    try {
      return new Intl.Locale(lang, { region: regionFromTimeZone() }).toString();
    } catch (e) {
      return lang.indexOf("-") === -1 ? lang + "-" + regionFromTimeZone() : lang;
    }
  }

  function matches(text) {
    var t = String(text || "").trim().toLowerCase();
    if (!t) return SUGGESTIONS.slice();
    if (config.filter_mode === "anywhere") {
      return SUGGESTIONS.filter(function (s) { return s.toLowerCase().indexOf(t) !== -1; });
    }
    return SUGGESTIONS.filter(function (s) { return s.toLowerCase().indexOf(t) === 0; });
  }

  function hide(el) { el.hidden = true; }
  function show(el) { el.hidden = false; }

  // ---- rendering ----------------------------------------------------------
  function applyFilter() {
    var typed = input.value.trim();
    var visible = matches(input.value);
    items.forEach(function (li) {
      li.hidden = visible.indexOf(li.textContent.trim()) === -1;
    });
    // Visible only once the user has typed something that matches at least one suggestion.
    list.hidden = listSuppressed || typed === "" || visible.length === 0;
  }

  function selectSuggestion(value) {
    input.value = value;
    listSuppressed = true;   // selecting closes the list until the user types again
    applyFilter();
    hide(errorEl);
    hide(successEl);
    input.focus();
  }

  function clearForm() {
    input.value = "";
    listSuppressed = true;   // Escape closes the suggestion list
    applyFilter();
    hide(errorEl);
    hide(successEl);
  }

  // ---- submission -------------------------------------------------------
  function submit() {
    hide(errorEl);
    hide(successEl);

    var payload = {
      text: input.value.trim(),
      start_date: startDate,
      end_date: toLocalISO(new Date()),
      locale: resolveLocale(),
      suggestion_list: matches(input.value).join(", ")
    };

    fetch(API_BASE + "/api/response", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (res) { (res.status === 200 ? show(successEl) : show(errorEl)); })
      .catch(function () { show(errorEl); });
  }

  // ---- events --------------------------------------------------------
  input.addEventListener("input", function () {
    listSuppressed = false;   // the user is typing -> allow the list to show
    hide(errorEl);
    hide(successEl);
    applyFilter();
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); submit(); }
    else if (e.key === "Escape") { e.preventDefault(); clearForm(); }
  });

  list.addEventListener("click", function (e) {
    var li = e.target.closest("li");
    if (li) selectSuggestion(li.textContent.trim());
  });

  list.addEventListener("keydown", function (e) {
    var li = e.target.closest("li");
    if (!li) return;
    if (e.key === "Enter") { e.preventDefault(); selectSuggestion(li.textContent.trim()); }
    else if (e.key === "Escape") { e.preventDefault(); clearForm(); input.focus(); }
  });

  nextBtn.addEventListener("click", submit);
  nextBtn.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { e.preventDefault(); clearForm(); }
  });

  // ---- init ---------------------------------------------------------
  fetch(API_BASE + "/api/config")
    .then(function (r) { return r.json(); })
    .then(function (c) { config = c; applyFilter(); })
    .catch(function () { applyFilter(); });

  // Small hook for debugging / manual exploration in the console.
  window.__APP__ = {
    toLocalISO: toLocalISO,
    resolveLocale: resolveLocale,
    get config() { return config; }
  };
})();
