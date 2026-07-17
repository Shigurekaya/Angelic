(() => {
  const D = window.UI_DATA;
  if (!D) {
    document.body.textContent = "缺少 data.js（运行 Angelic/tools/build_ui_preview.py）";
    return;
  }

  const state = {
    screen: "title",
    tab: "0",
    values: {},
    bgIndex: 0,
    pixel: D.settings && D.settings.pixel_ui_default !== false,
  };
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const W = (D.resolution && D.resolution.width) || 1920;
  const H = (D.resolution && D.resolution.height) || 1080;

  function toast(msg) {
    const el = $("#toast");
    el.hidden = false;
    el.textContent = msg;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => {
      el.hidden = true;
    }, 1400);
  }

  function setBg(el, src) {
    if (el && src) el.style.backgroundImage = 'url("' + src + '")';
  }

  function val(key, defVal) {
    if (!(key in state.values)) state.values[key] = defVal;
    return state.values[key];
  }

  function badge() {
    const srcs = (D[state.screen] && D[state.screen].sources) || [];
    const m = D.manifest || {};
    $("#badge").textContent =
      "Angelic · " + srcs.slice(0, 2).join(" · ") + (m.packs ? " · packs " + m.packs : "");
  }

  function showScreen(name) {
    state.screen = name;
    $$(".screen").forEach((s) => s.classList.toggle("active", s.id === "screen-" + name));
    location.hash = name;
    badge();
  }

  function syncPixelMode() {
    document.body.classList.toggle("is-pixel", state.pixel);
    const chk = $("#chk-pixel");
    if (chk) chk.checked = state.pixel;
  }

  function route(action, label) {
    if (action === "settings") showScreen("settings");
    else if (action === "load") showScreen("load");
    else if (action === "flowchart") showScreen("flowchart");
    else if (action === "cg") showScreen("cg");
    else if (action === "start") toast("开始游戏（预览）");
    else toast(label || action);
  }

  function renderTitle() {
    $("#game-name").textContent = D.game;
    const bgs = (D.title && D.title.backgrounds) || [];
    if (bgs.length) {
      state.bgIndex = Math.min(state.bgIndex, bgs.length - 1);
      setBg($("#title-bg"), bgs[state.bgIndex].src);
      const sw = $("#bg-switch");
      if (sw) {
        sw.innerHTML = "";
        bgs.forEach((bg, i) => {
          const b = document.createElement("button");
          b.type = "button";
          b.textContent = String(i + 1);
          b.classList.toggle("active", i === state.bgIndex);
          b.addEventListener("click", () => {
            state.bgIndex = i;
            setBg($("#title-bg"), bg.src);
            $$("#bg-switch button").forEach((x, j) => x.classList.toggle("active", j === i));
            toast("标题背景 " + (i + 1));
          });
          sw.appendChild(b);
        });
      }
    } else {
      setBg($("#title-bg"), D.title.bg);
    }
    const logo = $("#title-logo");
    if (logo && D.title.logo) {
      logo.src = D.title.logo;
      logo.hidden = false;
    }
    const nav = $("#title-menu");
    nav.innerHTML = "";
    (D.title.buttons || []).forEach((btn) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = btn.label;
      b.addEventListener("click", () => route(btn.action, btn.label));
      nav.appendChild(b);
    });
  }

  function renderPixelHits(hits) {
    const layer = $("#settings-hits");
    if (!layer) return;
    layer.innerHTML = "";
    (hits || []).forEach((h) => {
      const box = document.createElement("div");
      box.className = "hit";
      box.style.left = (h.x / W) * 100 + "%";
      box.style.top = (h.y / H) * 100 + "%";
      box.style.width = (h.w / W) * 100 + "%";
      box.style.height = (h.h / H) * 100 + "%";

      const title = document.createElement("div");
      title.className = "hl";
      title.textContent = h.label;
      const key = document.createElement("div");
      key.className = "hk";
      key.textContent = h.key;
      box.appendChild(title);
      box.appendChild(key);

      if (h.type === "slider") {
        const row = document.createElement("div");
        row.className = "row";
        const input = document.createElement("input");
        input.type = "range";
        input.min = "0";
        input.max = "100";
        input.value = String(val(h.key, 70));
        const num = document.createElement("span");
        num.className = "num";
        num.textContent = input.value;
        input.addEventListener("input", (e) => {
          e.stopPropagation();
          state.values[h.key] = Number(input.value);
          num.textContent = input.value;
        });
        input.addEventListener("click", (e) => e.stopPropagation());
        row.appendChild(input);
        row.appendChild(num);
        box.appendChild(row);
      } else {
        const opts = h.options || ["关", "开"];
        const on = !!val(h.key, false);
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "tog" + (on ? " on" : "");
        btn.textContent = on ? opts[1] || "开" : opts[0] || "关";
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          state.values[h.key] = !state.values[h.key];
          const now = !!state.values[h.key];
          btn.classList.toggle("on", now);
          btn.textContent = now ? opts[1] || "开" : opts[0] || "关";
          toast(h.label + " → " + btn.textContent);
        });
        box.appendChild(btn);
      }
      layer.appendChild(box);
    });
  }

  function renderFallbackRows(rows) {
    const box = $("#tab-content");
    if (!box) return;
    box.innerHTML = "";
    (rows || []).forEach((row) => {
      const wrap = document.createElement("div");
      wrap.className = "ctrl";
      wrap.innerHTML = '<div class="l"></div><div class="k"></div>';
      wrap.querySelector(".l").textContent = row.label;
      wrap.querySelector(".k").textContent = row.key;
      if (row.type === "slider") {
        const input = document.createElement("input");
        input.type = "range";
        input.min = "0";
        input.max = "100";
        input.value = String(val(row.key, 70));
        input.style.width = "100%";
        input.style.marginTop = "8px";
        input.addEventListener("input", () => {
          state.values[row.key] = Number(input.value);
        });
        wrap.appendChild(input);
      } else {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "tog" + (val(row.key, false) ? " on" : "");
        btn.textContent = val(row.key, false) ? "开" : "关";
        btn.style.marginTop = "8px";
        btn.addEventListener("click", () => {
          state.values[row.key] = !state.values[row.key];
          btn.classList.toggle("on", !!state.values[row.key]);
          btn.textContent = state.values[row.key] ? "开" : "关";
        });
        wrap.appendChild(btn);
      }
      box.appendChild(wrap);
    });
    const help = $("#help");
    if (help) help.textContent = "中文对照面板\n来源: option*.pbd / uitexts_cn";
  }

  function renderSettings() {
    setBg($("#settings-bg"), D.settings.bg);
    const chassis = $("#settings-chassis");
    if (chassis && D.settings.chassis) chassis.src = D.settings.chassis;

    const tabs = D.settings.tabs || [];
    if (!tabs.find((t) => t.id === state.tab) && tabs[0]) state.tab = tabs[0].id;
    const bar = $("#tab-bar");
    bar.innerHTML = "";
    tabs.forEach((t) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = t.label;
      b.classList.toggle("active", t.id === state.tab);
      b.addEventListener("click", () => {
        state.tab = t.id;
        renderSettingsBody();
        $$("#tab-bar button").forEach((x, i) => x.classList.toggle("active", tabs[i].id === state.tab));
      });
      bar.appendChild(b);
    });
    if (D.settings.footer) {
      const bt = $("#btn-back-title");
      if (bt) bt.textContent = D.settings.footer.back_title || "返回标题";
    }
    renderSettingsBody();
  }

  function renderSettingsBody() {
    const tab = (D.settings.tabs || []).find((t) => t.id === state.tab) || (D.settings.tabs || [])[0];
    const fallback = $("#settings-fallback");
    if (tab && tab.mode === "pixel" && tab.hotspots) {
      renderPixelHits(tab.hotspots);
      document.body.classList.add("is-pixel");
      if (fallback) fallback.hidden = true;
    } else {
      renderPixelHits([]);
      renderFallbackRows(tab && tab.rows);
      document.body.classList.remove("is-pixel");
      if (fallback) fallback.hidden = false;
    }
    syncPixelMode();
    if (tab && tab.mode === "pixel") document.body.classList.add("is-pixel");
  }

  function renderLoad() {
    setBg($("#load-bg"), D.load.bg);
    const pack = $("#load-pack");
    if (pack && D.load.pack) pack.src = D.load.pack;
    if (D.load.title) {
      const t = $("#load-title");
      if (t) t.textContent = D.load.title;
    }
    const grid = $("#slot-grid");
    grid.innerHTML = "";
    for (let i = 1; i <= (D.load.slots || 12); i++) {
      const s = document.createElement("button");
      s.type = "button";
      s.className = "slot";
      s.innerHTML =
        '<div class="n">No.' + String(i).padStart(2, "0") + '</div><div class="t">空数据</div>';
      s.addEventListener("click", () => {
        $$(".slot").forEach((x) => x.classList.remove("active"));
        s.classList.add("active");
        toast("读取存档槽 " + i);
      });
      grid.appendChild(s);
    }
  }

  function renderFlow() {
    setBg($("#flowchart-bg"), D.flowchart.bg);
    const pack = $("#flowchart-pack");
    if (pack && D.flowchart.pack) pack.src = D.flowchart.pack;
    if (D.flowchart.title) {
      const t = $("#flow-title");
      if (t) t.textContent = D.flowchart.title;
    }
    const box = $("#flow-nodes");
    box.innerHTML = "";
    (D.flowchart.nodes || []).forEach((name) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = name;
      b.addEventListener("click", () => {
        if (String(name).indexOf("返回") >= 0) showScreen("title");
        else toast("流程图：" + name);
      });
      box.appendChild(b);
    });
  }

  function renderCg() {
    setBg($("#cg-bg"), D.cg.bg);
    const pack = $("#cg-pack");
    if (pack && D.cg.pack) pack.src = D.cg.pack;
    if (D.cg.title) {
      const t = $("#cg-title");
      if (t) t.textContent = D.cg.title;
    }
    const grid = $("#cg-grid");
    grid.innerHTML = "";
    (D.cg.items || []).forEach((name, i) => {
      const s = document.createElement("button");
      s.type = "button";
      s.className = "cg-item";
      s.innerHTML =
        '<div class="n">#' + String(i + 1).padStart(2, "0") + '</div><div class="t">' + name + "</div>";
      s.addEventListener("click", () => {
        $$(".cg-item").forEach((x) => x.classList.remove("active"));
        s.classList.add("active");
        toast("鉴赏：" + name);
      });
      grid.appendChild(s);
    });
  }

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-nav]");
    if (!btn) return;
    showScreen(btn.getAttribute("data-nav"));
  });

  const chk = $("#chk-pixel");
  if (chk) {
    chk.addEventListener("change", () => {
      state.pixel = chk.checked;
      renderSettingsBody();
    });
  }

  document.title = D.game + " · Angelic UI";
  syncPixelMode();
  renderTitle();
  renderSettings();
  renderLoad();
  renderFlow();
  renderCg();
  const h = (location.hash || "#title").replace("#", "");
  showScreen(["title", "settings", "load", "flowchart", "cg"].includes(h) ? h : "title");
})();
