// Shared behaviour: mobile menu, scrollable tables, contents panel for the long reports.
(function () {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  document.querySelectorAll("main table").forEach((table) => {
    if (table.parentElement.classList.contains("table-wrap")) return;
    const wrap = document.createElement("div");
    wrap.className = "table-wrap";
    wrap.tabIndex = 0;
    wrap.setAttribute("role", "region");
    wrap.setAttribute("aria-label", "Scrollable table");
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });

  const toc = document.querySelector(".toc ol");
  const article = document.querySelector(".report-body");
  if (toc && article) {
    const heads = [...article.querySelectorAll("h2")];
    heads.forEach((h, i) => {
      if (!h.id) h.id = "s" + (i + 1);
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = h.textContent.replace(/^\d+\.\s*/, "");
      li.appendChild(a);
      toc.appendChild(li);
    });
    const links = [...toc.querySelectorAll("a")];
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          links.forEach((l) => l.classList.toggle("active", l.getAttribute("href") === "#" + e.target.id));
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    heads.forEach((h) => spy.observe(h));
  }
})();
