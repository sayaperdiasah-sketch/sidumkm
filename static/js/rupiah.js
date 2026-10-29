/* SIDUMKM — format rupiah manual + bulatkan ke Rp1.000 (dipakai form rencana & produk) */
(function () {
  "use strict";
  (function () {
  "use strict";
  function pasang(el) {
    el.addEventListener("input", function () {
      var v = parseInt((el.value || "").replace(/\D/g, "") || "0", 10);
      el.value = v ? v.toLocaleString("id-ID") : "";
    });
    el.addEventListener("blur", function () {
      var v = parseInt((el.value || "").replace(/\D/g, "") || "0", 10);
      if (!v) { el.value = ""; return; }
      var bulat = Math.round(v / 1000) * 1000;
      el.value = bulat ? bulat.toLocaleString("id-ID") : String(v);
    });
  }
  document.querySelectorAll("input.rupiah").forEach(pasang);
})();
