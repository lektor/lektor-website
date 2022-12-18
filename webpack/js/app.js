// @ts-check

import "bootstrap";

function initDownloadButton() {
  const downloadLink = document.querySelector(".download-btn a");
  if (downloadLink) {
    // See https://warehouse.pypa.io/api-reference/json.html#project
    fetch("https://pypi.org/pypi/lektor/json", { method: "GET" })
      .then((res) => res.json())
      .then((project) => {
        const version = project.info.version;
        const span = document.createElement("span");
        span.className = "version";
        span.innerText = version;
        downloadLink.append(span);
      })
      .catch((err) => {
        console.error(
          "fetching the latest Lektor version from the Github API failed: ",
          err
        );
      });
  }
}

function initGoogleSearch() {
  const container = document.querySelector(".google-custom-search");
  if (!container) {
    return;
  }
  const cx = "012722186170730423054:utwznhnrrmi";
  const gcse = document.createElement("script");
  gcse.type = "text/javascript";
  gcse.async = true;
  gcse.src =
    (document.location.protocol == "https:" ? "https:" : "http:") +
    "//cse.google.com/cse.js?cx=" +
    cx;
  const firstScript = document.getElementsByTagName("script")[0];
  if (!firstScript || !firstScript.parentNode) {
    return;
  }
  firstScript.parentNode.insertBefore(gcse, firstScript);

  container.insertAdjacentHTML(
    "beforeend",
    `<gcse:searchresults-only linktarget="_parent"></gcse:searchresults-only>`
  );
  container.insertAdjacentHTML(
    "beforeend",
    `
  <div style="display: none">
    <div id="base_webResult">
      <div class="gs-webResult gs-result"
        data-vars="{
          longUrl: function() {
            var i = unescapedUrl.indexOf(visibleUrl);
            return i < 1 ? visibleUrl : unescapedUrl.substring(i);
          },
          processSearchTitle: function(title) {
            return title.split(' | ').slice(0, -2).join(' | ') || 'Documentation';
          }
        }">
        <div class="gs-title">
          <a class="gs-title" data-attr="{href:unescapedUrl, target:target}"
            data-body="html(processSearchTitle(title))"></a>
        </div>
        <div class="gs-visibleUrl gs-visibleUrl-long" data-body="longUrl()"></div>
        <div class="gs-snippet" data-body="html(content)"></div>
      </div>
    </div>
  </div>
  `
  );

  const params = new URLSearchParams(location.search);
  const query = params.get("q");
  if (query) {
    const input = container.querySelector('input[name="q"]');
    if (input instanceof HTMLInputElement) {
      input.value = query;
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  initDownloadButton();
  initGoogleSearch();
});
