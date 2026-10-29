/* SIDUMKM — form catat uang: sekali klik, tanpa istilah teknis */
(function () {
  "use strict";
  var form = document.getElementById("form-catat");
  if (!form) return;

  var jenis = form.querySelector("#jenis");
  var jumlah = form.querySelector("#jumlah");
  var bilang = form.querySelector("#bilang");
  var pil = form.querySelectorAll(".pil");

  function digit() { return (jumlah.value || "").replace(/\D/g, ""); }

  function tampil() {
    var v = parseInt(digit() || "0", 10);
    jumlah.value = v ? v.toLocaleString("id-ID") : "";
    if (bilang) bilang.textContent = v ? "Rp " + v.toLocaleString("id-ID") : "Rp 0 — tinggal tekan Simpan";
  }

  function pilihJenis(nilai) {
    jenis.value = nilai;
    pil.forEach(function (t) {
      var aktif = t.getAttribute("data-jenis") === nilai;
      t.setAttribute("aria-pressed", aktif ? "true" : "false");
      t.classList.toggle("aktif", aktif);
    });
    document.querySelectorAll("[data-grup-jenis]").forEach(function (g) {
      g.hidden = g.getAttribute("data-grup-jenis") !== nilai;
    });
  }

  pil.forEach(function (t) {
    t.type = "button";
    t.addEventListener("click", function () { pilihJenis(t.getAttribute("data-jenis")); });
  });

  document.querySelectorAll(".chip").forEach(function (c) {
    c.type = "button";
    c.addEventListener("click", function () {
      pilihJenis(c.getAttribute("data-jenis"));
      jumlah.value = c.getAttribute("data-jumlah");
      tampil();
      form.querySelector(".simpan-besar").focus();
    });
  });

  jumlah.addEventListener("input", tampil);
  jumlah.addEventListener("blur", function () {
    var v = parseInt(digit() || "0", 10);
    if (!v) { jumlah.value = ""; tampil(); return; }
    jumlah.value = (Math.round(v / 500) * 500).toLocaleString("id-ID");  // bulat ke Rp500
    tampil();
  });
  jumlah.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); form.requestSubmit(form.querySelector(".simpan-besar")); }
  });

  /* kirim angka polos ke server, bukan "12.000" */
  form.addEventListener("submit", function () { jumlah.value = digit(); });

  pilihJenis(jenis.value || "masuk");
  tampil();
})();
