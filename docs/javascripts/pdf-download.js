(function () {
  var BAR_CLASS = "nexus-pdf-bar";
  var BTN_CLASS = "nexus-pdf-btn";

  function pdfCandidatesForCurrentPage() {
    /* Material uses directory-style URLs by default:
         docs/foo/bar.md  ->  site/foo/bar/index.html  ->  URL /foo/bar/
         mkdocs-pdf-export-plugin writes the PDF as <dir>/<src-basename>.pdf
         For docs/index.md (URL /) the PDF is /index.pdf */
    var path = window.location.pathname;
    if (!path.endsWith("/")) path = path + "/";
    var trimmed = path.replace(/\/$/, "");
    var lastSegment = trimmed.substring(trimmed.lastIndexOf("/") + 1);
    var candidates = [];
    if (lastSegment) {
      candidates.push(path + lastSegment + ".pdf");
    }
    candidates.push(path + "index.pdf");
    return candidates;
  }

  function pdfFilenameForDownload() {
    var trimmed = window.location.pathname.replace(/\/$/, "");
    var slug = trimmed.substring(trimmed.lastIndexOf("/") + 1) || "nexus-document";
    return slug + ".pdf";
  }

  function probePdf(url) {
    return fetch(url, { method: "HEAD", cache: "no-cache" })
      .then(function (r) {
        return r.ok ? url : null;
      })
      .catch(function () {
        return null;
      });
  }

  function findPdf() {
    var candidates = pdfCandidatesForCurrentPage();
    var i = 0;
    function next() {
      if (i >= candidates.length) return Promise.resolve(null);
      var c = candidates[i++];
      return probePdf(c).then(function (found) {
        return found || next();
      });
    }
    return next();
  }

  function triggerDownload(url) {
    var a = document.createElement("a");
    a.href = url;
    a.download = pdfFilenameForDownload();
    a.rel = "noopener";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  function handleClick(btn) {
    btn.disabled = true;
    findPdf().then(function (url) {
      btn.disabled = false;
      if (url) {
        triggerDownload(url);
      } else {
        window.print();
      }
    });
  }

  function init() {
    var inner = document.querySelector(".md-content__inner");
    if (!inner) return;
    if (inner.querySelector("." + BAR_CLASS)) return;

    var bar = document.createElement("div");
    bar.className = BAR_CLASS;

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = BTN_CLASS;
    btn.setAttribute("aria-label", "Download this page as PDF");
    btn.setAttribute("title", "Download as PDF");
    btn.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">' +
      '<path fill="currentColor" d="M5 20h14v-2H5v2zM12 3 5.33 11.33l1.34 1.34L11 8.34V17h2V8.34l4.33 4.33 1.34-1.34L12 3z" transform="rotate(180 12 12)"/>' +
      "</svg>" +
      "<span>Download PDF</span>";

    btn.addEventListener("click", function () {
      handleClick(btn);
    });

    bar.appendChild(btn);
    inner.insertAdjacentElement("afterbegin", bar);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
