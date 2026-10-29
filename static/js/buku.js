/* SIDUMKM — interaksi ringan (animasi skor, saring buku kas, lihat sandi) */
(function () {
  "use strict";
  var hemat = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* 1. Busur skor: dashoffset digeser supaya teranimasi dari nol */
  var isi = document.querySelector(".meter__isi");
  if (isi) {
    var target = parseFloat(isi.getAttribute("data-isi") || "0");
    if (!hemat) {
      isi.style.strokeDashoffset = "100";
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { isi.style.strokeDashoffset = String(100 - target); });
      });
    }
  }

  /* 2. Angka skor ikut menghitung naik (satu desimal, koma Indonesia) */
  var angka = document.querySelector(".meter__angka");
  if (angka) {
    var tujuan = parseFloat(angka.getAttribute("data-angka") || "0");
    var des = parseInt(angka.getAttribute("data-desimal") || "0", 10);
    var tulis = function (v) { angka.textContent = v.toFixed(des).replace(".", ","); };
    if (hemat) {
      tulis(tujuan);
    } else {
      var mulai = performance.now(), durasi = 1100;
      var langkah = function (t) {
        var p = Math.min(1, (t - mulai) / durasi);
        tulis(tujuan * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(langkah);
      };
      requestAnimationFrame(langkah);
    }
  }

  /* 3. Saring baris buku kas */
  var saring = document.getElementById("saring-buku");
  if (saring) {
    saring.addEventListener("input", function () {
      var q = this.value.trim().toLowerCase();
      document.querySelectorAll("[data-buku] tr").forEach(function (tr) {
        tr.hidden = q ? tr.textContent.toLowerCase().indexOf(q) === -1 : false;
      });
    });
  }

  /* 4. Tombol lihat sandi */
  document.querySelectorAll(".sandi-liat button").forEach(function (t) {
    t.addEventListener("click", function () {
      var input = t.parentElement.querySelector("input");
      var lihat = input.type === "password";
      input.type = lihat ? "text" : "password";
      t.textContent = lihat ? "Sembunyi" : "Lihat";
    });
  });

  /* 5. Form cepat: langsung kembali ke atas daftar setelah menyimpan */
  if (location.hash === "#buku") {
    var t = document.getElementById("buku");
    if (t) t.scrollIntoView();
  }

  /* 6. Semua tombol "hapus" minta kepastian lebih dulu */
  document.querySelectorAll("[data-konfirmasi]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-konfirmasi"))) e.preventDefault();
    });
  });
})();
