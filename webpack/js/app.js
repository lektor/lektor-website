// @ts-check

require("bootstrap");
var qs = require("query-string");

function selectText(text) {
  if (document.body.createTextRange) {
    let range = document.body.createTextRange();
    range.moveToElementText(text);
    range.select();
  } else if (window.getSelection) {
    let selection = window.getSelection();
    let range = document.createRange();
    range.selectNodeContents(text);
    selection.removeAllRanges();
    selection.addRange(range);
  }
}

function initBadges() {
  let badges = $(".badges li").hide();
  if (badges.length > 0) {
    window.setTimeout(function () {
      badges.fadeIn(500);
    }, 1500);
  }
}

function initDownloadButton() {
  const buttons = $(".download-btn");
  if (buttons.length <= 0) {
    return;
  }

  buttons.hide();
  $.ajax({
    method: "GET",
    url: "https://api.github.com/repos/lektor/lektor/releases",
    crossDomain: true,
  }).then(
    (releases) => {
      updateDownloadButtons(buttons.toArray(), releases);
    },
    () => {
      buttons.show();
    }
  );
}

function updateDownloadButtons(buttons, releases) {
  let tag = releases[0].tag_name;

  buttons.forEach((button) => {
    let link = $("a", button);

    link.attr("href", "/downloads/");
    link.append($('<span class="version"></span>').text(tag));

    $(button).fadeIn("slow");
  });
}

function initInstallRow() {
  let code = $(".install-row pre");
  if (code.length > 0) {
    code.on("dblclick", function () {
      selectText(this);
    });
  }
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

  var params = qs.parse(location.search);
  if (params.q) {
    $('input[name="q"]', container).val(params.q);
  }
}

function hideThingsForWindows() {
  if (navigator.appVersion.indexOf("Win") >= 0) {
    $(".hide-for-windows").hide();
  }
}

$(function () {
  initBadges();
  initDownloadButton();
  initInstallRow();
  initGoogleSearch();
  hideThingsForWindows();
});
