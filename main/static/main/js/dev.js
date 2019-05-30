function loadTab(url, tabSaveName) {
        var currentTab = sessionStorage.getItem('sandboxControlPanelTab');
        $.ajax({
            dataType: "text",
            url: "/" + url,
            // When the data is received from the request, do this:
            success: function (result) {
                $("#content").html(result.toString());
                // Save the current tab
                sessionStorage.setItem(tabSaveName, url);
            }
        })
    }

/**
 * Functionaly for control panels.
  * @param tabSaveName Name to use when saving the current tab to sessionStorage.
 * @param defaultTab Default tab to start on if there is not tab saved.
 */
function controlPanel(tabSaveName, defaultTab){

    var tab = sessionStorage.getItem(tabSaveName);
    if (tab === null || tab === "undefined" ) {
        tab = defaultTab
    }

    loadTab(tab, tabSaveName);

    // When a nav link is clicked on...
      $("#controlPanel > .navlink").click(function () {
          $(".active").removeClass("active");
          $(this).addClass("active");
          loadTab(this.id, tabSaveName)
      });
}

function changeCompanyName() {
    $.ajax({
            dataType: 'text',
            url: '/dev/account/changecompanyname/',
            success: function (result) {
                $('#companyName').html(result)
            }
        })
}

function cancelChangeCompanyName() {
    $.ajax({
        dataType: 'text',
        url: '/dev/account/companyname/',
        success: function (result) {
            $('#companyName').html(result);
            $("#changeCompanyName").click(changeCompanyName)
        }
    })
}

function companyName(){
    $("#changeCompanyName").click(changeCompanyName)
}


var matchTypeId;
var maxMatchLength;

function changeMaxMatchLength() {
    $.ajax({
        dataType: 'text',
        url: '/dev/sandbox/changemaxmatchlength/',
        success: function (result) {
            $('#maxMatchLength').html(result);
            $('#changeMaxMatchLength').click(changeMaxMatchLength);
            $("#changeMaxMatchLengthButton").click(sendChangeMaxMatchLength)
        }
    })
}

function sendChangeMaxMatchLength() {
    $.post("/dev/sandbox/changemaxmatchlength/", {
        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
        maxMatchLength: $('#changeMaxMatchLengthInput').val(),
        matchTypeId: matchTypeId

    }).done(
        function(result) {
            console.log(result);
            $('#maxMatchLength').html(result);
            $("#changeMaxMatchLength").click(changeMaxMatchLength);
        }
    ).fail(function (result) {
        $("#errorMessage").html(result.responseText)
    })
}

function cancelChangeMaxMatchLength() {
    $.ajax({
        dataType: 'text',
        url: '/dev/sandbox/maxmatchlength/',
        success: function (result) {
            $('#maxMatchLength').html(result);
            $("#changeMaxMatchLength").click(changeMaxMatchLength);
            $("#maxMatchLengthLabel").html("Max Match Length: " + maxMatchLength);
        }
    })
}

function maxMatchLength(id, maxMatchL) {
    matchTypeId = id;
    maxMatchLength = maxMatchL;
    $("#changeMaxMatchLength").click(changeMaxMatchLength)
}

