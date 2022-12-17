// @ts-check

require("bootstrap");

function initDownloadButton() {
  const buttons = $(".download-btn");
  if (buttons.length <= 0) {
    return;
  }

  $.ajax({
    method: "GET",
    url: "https://api.github.com/repos/lektor/lektor/releases",
    crossDomain: true,
  }).then((releases) => {
    updateDownloadButtons(buttons.toArray(), releases);
  });
}

function updateDownloadButtons(buttons, releases) {
  let tag = releases[0].tag_name;

  buttons.forEach((button) => {
    let link = $("a", button);

    link.attr("href", "/downloads/");
    link.append($('<span class="version"></span>').text(tag));
  });
}

function initGoogleSearch() {
  var container = $(".google-custom-search");
  if (container.length == 0) {
    return;
  }
  var cx = "012722186170730423054:utwznhnrrmi";
  var gcse = document.createElement("script");
  gcse.type = "text/javascript";
  gcse.async = true;
  gcse.src =
    (document.location.protocol == "https:" ? "https:" : "http:") +
    "//cse.google.com/cse.js?cx=" +
    cx;
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(gcse, s);

  $(`
    <gcse:searchresults-only linktarget="_parent"></gcse:searchresults-only>
  `).appendTo(container);
  $(`
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
  `).appendTo(container);

  const params = new URLSearchParams(location.search);
  const query = params.get("q");
  if (query) {
    $('input[name="q"]', container).val(query);
  }
}

$(function () {
  initDownloadButton();
  initGoogleSearch();
});
