/*
Copyright © 2017 Jan Frömberg, Laura Höhle (http://www.gerdi-project.de)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/*jshint esversion: 6 */

// currentTheme, startView and sessionUrl are set in bottom of base.html

// set global variables for the current viewtype
var listView, cardView, tableView;
listView = startView === 'list';
cardView = startView === 'card';
tableView = startView === 'table';

/*
   Execute when DOM is ready
*/
$(function () {

    $('#loaderSpinnerLog').hide();
    $('#loaderSpinnerStat').hide();

    if ($('#collapseChart').is(':visible')) {
        loadChart();
    }

    resizeFunction();
    toggleViews();
    initTheme();

    var ctx = document.getElementById("harvesterChart");
    if (ctx != null) {
        var myChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['my_label'],
                datasets: [{
                    label: 'Number of harvested Items',
                    data: [170482],
                    backgroundColor: ['rgba(255, 99, 132, 0.2)'],
                    borderColor: ['rgba(255, 99, 132, 1)'],
                    borderWidth: 1
                }]
            },
            options: {
                cutoutPercentage: 45
            }
        });
    }

    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });

    $(function () {
        $('[data-toggle="popover"]').popover();
    });

    function load_into_modal(_this) {
        var url = $(_this).attr("title");
        $('#loaderSpinnerLog').show();
        $.getJSON(url, function (result) {
            var status = result;
            var data = JSON.stringify(result, undefined, 2);
            $('#message-modal-footer').show();
            $('#message-modal').modal('toggle');
            $('#message-modal-body').html('<pre>' + data + '</pre>');
            for (let key in status) {
                let obj = status[key];
                $('#hv-status-' + key).html(obj.log);
            }
            $('#loaderSpinnerLog').hide();

        }).fail(function (response) {
            $('#loaderSpinnerLog').hide();
            $('#message-modal-footer').show();
            $('#message-modal').modal('toggle');
            $('#message-modal-body').html(response.responseText);
        });
    }

    function updateChart(labels, data, bgColorArray, bColorArray) {

        $('#loaderSpinnerStat').hide();

        myChart.data.labels.pop();
        myChart.data.datasets.forEach(function (dataset) {
            dataset.data.pop();
            dataset.backgroundColor.pop();
            dataset.borderColor.pop();
        });
        myChart.update();

        myChart.data.labels = labels;
        myChart.data.datasets[0].backgroundColor = bgColorArray;
        myChart.data.datasets[0].borderColor = bColorArray;
        myChart.data.datasets[0].data = data;
        myChart.update();
    }

    function updateGUI(data) {

        var status = data;
        var vdata = [];
        var vlabels = [];
        var gbcarray = [];
        var bcarray = [];

        for (var key in status) {

            var obj = status[key];
            if (obj != 'disabled') {

                $('#hv-status-' + key).html(JSON.stringify(obj));
                var btnhvstatus = document.getElementById('btn-harvester-status-' + key);
                if (btnhvstatus) {
                    btnhvstatus.classList.toggle("btn-info", false);
                    btnhvstatus.classList.toggle("btn-warning", false);
                    btnhvstatus.classList.toggle("btn-success", false);
                    btnhvstatus.classList.add("btn-" + obj.gui_status);
                }
                if (obj.status) {
                    var lbl_status = document.getElementById('lbl-harvester-status-' + key);
                    lbl_status.innerHTML = obj.status;
                }
                if (obj.cached_docs) {
                    vlabels.push(key);
                    vdata.push(parseInt(obj.cached_docs));
                    var r = (Math.floor(Math.random() * 256));
                    var g = (Math.floor(Math.random() * 256));
                    var b = (Math.floor(Math.random() * 256));
                    gbcarray.push('rgba(' + r + ',' + g + ',' + b + ',0.3)');
                    bcarray.push('rgba(' + r + ',' + g + ',' + b + ',0.4)');
                }
                if (obj.health != 'OK') {
                    $('#health-exclamation-' + key).show();
                    $('#health-exclamation-' + key).prop('title', obj.health);
                } else {
                    $('#health-exclamation-' + key).hide();
                }
                if (obj.status == 'harvesting') {
                    //$( '#progresshv-' + key ).show();
                } else {
                    //$( '#progresshv-' + key ).hide();
                }
                if (obj.data_pvd) {
                    $('#btn-harvester-status-' + key).attr('data-original-title', obj.data_pvd +
                        ' harvested and cached documents: ' +
                        obj.cached_docs + ' of ' +
                        obj.max_docs + '. Last harvest: ' +
                        obj.lastHarvestDate);
                }
            }
        }

        updateChart(vlabels, vdata, gbcarray, bcarray);
    }

    function loadChart() {
        var url = $('#collapseChart').attr("title");
        $('#loaderSpinnerStat').show();
        $.get(url, function (result) {

            updateGUI(result);

        }).fail(function (response) {

            $('#loaderSpinnerStat').hide();
            $('#message-modal-footer').show();
            $('#message-modal').modal('toggle');
            $('#message-modal-body').html(response.responseText);

        });
    }

    $('#collapseChart').on('show.bs.collapse', function (event) {
        updateSession('chart', 'visible');
        loadChart();
    });

    $('#collapseChart').on('hide.bs.collapse', function () {
        updateSession('chart', 'collapsed');
    });

    $('#collapseToolbox').on('show.bs.collapse', function () {
        updateSession('toolbox', 'visible');
    });

    $('#collapseToolbox').on('hide.bs.collapse', function () {
        updateSession('toolbox', 'collapsed');
    });

    $('#collapseHarvestersDisabled').on('show.bs.collapse', function() {
        updateSession('disabled_harvs', 'visible');
    });

    $('#collapseHarvestersDisabled').on('hide.bs.collapse', function() {
        updateSession('disabled_harvs', 'collapsed');
    });
    
    $('#collapseHarvestersEnabled').on('show.bs.collapse', function() {
        // The if statement is needed, because otherwise updateSession will
        // be fired also when a inner div is collapsed
        if (!$(this).is(':visible')) {
            updateSession('enabled_harvs', 'visible');
        }
    });

    $('#collapseHarvestersEnabled').on('hidden.bs.collapse', function() {
        // The if statement is needed, because otherwise updateSession will
        // be fired also when a inner div is collapsed
        if ($(this).is(':hidden')) {
            updateSession('enabled_harvs', 'collapsed');
        }
    });

    /*
        Buttons
    */
    $('#btn-harvester-log').on('click', function (ev) {
        ev.preventDefault();
        let url = $(this).attr("title");
        $('#loaderSpinnerLog').show();
        $("#form-modal").load(url, function () {
            $(this).modal('show');
            $('#loaderSpinnerLog').hide();
        });
        return false;
    });

    $('#btn-hcc-log').on('click', function (event) {
        load_into_modal(this);
    });

    $('[id^=btn-url]').on('click', function (event) {
        load_into_modal(this);
    });

    $('.toggle-view-button').click(function () {
        // id is btn-(viewtype)-view
        var viewtype = $(this).attr('id').split('-')[1];

        // set global viewtype variables
        listView = viewtype === 'list';
        cardView = viewtype === 'card';
        tableView = viewtype === 'table';

        updateSession('viewtype', viewtype);

        // actually change the viewtype and check for filter
        toggleViews();
        filterFunction();
    });

    $(".harvesteredit").click(function (ev) { // for each edit harvester url
        ev.preventDefault(); // prevent navigation
        var url = $(this).attr("data-form"); // get the harvester form url
        $("#form-modal").load(url, function () { // load the url into the modal
            $(this).modal('show'); // display the modal on url load
        });
        return false; // prevent the click propagation
    });

    $(".harvesterconfig").click(function (ev) {
        ev.preventDefault();
        var url = $(this).attr("data-form");
        $("#form-modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });

    $('.crontab-edit-form').submit(function (ev) {
        ev.preventDefault();
        var serializedData = $(this).serialize();
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: serializedData,
            context: this,
            success: function (response) {
                $('#message-modal-header').text(response.status == 'Ok' ? 'Success!' : 'Error');
                $('#message-modal-body').text(response.message);
                $('#message-modal-exit').show();
                $('#message-modal-footer').hide();
                $('#message-modal').modal('show');
            },
            error: function (response) {
                $('#message-modal-header').text('Error!');
                $('#message-modal-body').text('There has been an internal error. Please contact an administrator.');
                $('#message-modal-exit').show();
                $('#message-modal-footer').hide();
                $('#message-modal').modal('show');
            },
        });
        return false;
    });

    $('.status-radio').click(function () {
        /*
        Related to the radio buttons in dropdown menu in table-view
        */
        if ($('#checkbox-show-all').prop('checked')) checkboxShowAll();
        if ($('#checkbox-show-idle').prop('checked')) checkboxShowIdle();
        if ($('#checkbox-hide-idle').prop('checked')) checkboxHideIdle();
    });

    $('#btn-load-harvester-data').click(function(ev) {
        ev.preventDefault();
        var url = $(this).attr("href");
        $("#form-modal").load(url, function () {
            $(this).modal('show');
        });
        return false;
    });

    $('#toggle-theme-button').click(function (ev) {
        ev.preventDefault();
        var theme;

        if ($('#toggle-theme-text').text().includes("Dark Theme")) {
            // changing from light to dark theme
            theme = 'dark';
            $('#toggle-theme-text').text("Light Theme");
            $('#toggle-theme-link').attr("href", "https://bootswatch.com/4/darkly/bootstrap.min.css");
        } else {
            // changing from dark to light theme
            theme = 'light';
            $('#toggle-theme-text').text("Dark Theme");
            $('#toggle-theme-link').attr("href", "https://bootswatch.com/4/materia/bootstrap.min.css");
        }

        $('.navbar').toggleClass("light-theme-bg dark-theme-bg");
        $('.footer').toggleClass("footer-light footer-dark");
        $('input').toggleClass("dark-input-fields");

        updateSession('theme', theme);
        return false;
    });
});

/*
   Execute when page/window is loaded
*/
$(window).ready(function () {

    getStatusHistories();

    // milisec to hours, min, sec
    var timeConvert = function (milis) {
        var milisec = milis;
        var rseconds = Math.floor((milisec / 1000) % 60);
        var rminutes = Math.floor((milisec / (1000 * 60)) % 60);
        var rhours = Math.round((milisec / (1000 * 60 * 60)) % 24);
        var rdays = Math.round(milisec / (1000 * 60 * 60 * 24));
        
        if (rdays == 0 && rhours == 0 && rminutes == 0) {
            return rseconds + "sec";
        } else if (rdays == 0 && rhours == 0) {
            return rminutes + "min " + rseconds + "sec";
        } else if (rdays == 0) {
            return rhours + "h " + rminutes + "min " + rseconds + "sec";
        } else {
            return rdays + "d" + rhours + "h " + rminutes + "min " + rseconds + "sec";
        }
    };

    var lbl_status = document.querySelectorAll('*[id^="lbl-harvester-status-"]');
    var lblarray = Array.from(lbl_status);
    if (lblarray.length > 0) {
        for (var key in lblarray) {

            var obj = lblarray[key];
            var objid = obj.id;
            var me = objid.split('-')[3];

            if (obj.innerText == 'harvesting' || obj.innerText == 'queued') {

                var is = $('#progresshv-' + me);
                is.addClass("progress-bar-animated");
                is.removeClass("progress-bar-grey");
                var remember = is.attr("title");
                var progressid = setInterval( getProgress, 1982, remember, me );
            }
        }
    }

    function getProgress(_url, _harv) {
        
        var bar = $( '#progresshv-' + _harv);
        var timelabel = $( '#status-label-' + _harv);
        var statuslabel = $( '#lbl-harvester-status-' + _harv);
        var btnhvstatus = document.getElementById('btn-harvester-status-' + _harv);
        var width = parseInt(bar[0].innerText.replace('%', ''));
        var state = statuslabel[0].innerText;
        var perc = "%";
        var remain, elapsed, activated;
        var time = 0;
        var time_string = "";
        var start, now;

        if (state == 'harvesting' || state == 'queued' || typeof state == "undefined") {

            var request = $.ajax({
                url: _url,
                headers: {
                    "Access-Control-Allow-Origin": "*"
                },
                xhrFields: {
                    withCredentials: true
                },
                dataType: 'json',
                method: 'GET'
            });

            request.done(function (data) {
                for (var key in data) {

                    width = data[key].progress_cur;
                    remain = data[key].remainingHarvestTime;
                    elapsed = data[key].lastHarvestDate;
                    activated = data[key].lastActivated;
                    max = data[key].max_docs;
                    cache = data[key].progress;
                    state = data[key].state;

                    $('#btn-harvester-status-' + key).attr('data-original-title',
                        cache + ' of ' + max);
                    $('.harvester-status-' + _harv).html(state);

                    // referenced by context, this
                    bar.css("width", width + "%");
                    if (max === "N/A") {
                        perc = "";
                    }
                    if (typeof remain !== "undefined") {
                        time = timeConvert(remain);
                        time_string = 'remaining time: ' + time;
                        timelabel.html( time_string );
                    } else if (typeof elapsed !== "undefined") {
                        start = new Date(elapsed);
                        now = new Date();
                        time = timeConvert(now - start);
                        time_string = 'current runtime: ' + time;
                        timelabel.html( time_string );
                    } else if (typeof activated !== "undefined") {
                        start = new Date(activated);
                        now = new Date();
                        time = timeConvert(now - start);
                        time_string = 'waiting for harvest: ' + time;
                        timelabel.html( time_string );
                    }
                    bar.html(width + perc);
                }
            });
            request.fail( function(data) {
                timelabel.html("waiting for the server to respond...");
            });

        } else {

            bar.removeClass("progress-bar-animated");
            bar.addClass("progress-bar-grey");
            bar.css("width", width + "%");
            bar.html(width + '%');
            btnhvstatus.classList.toggle( "btn-info", false );
            btnhvstatus.classList.toggle( "btn-primary", false );
            btnhvstatus.classList.add( "btn-success" );
            timelabel.html( "" );
            statuslabel.html("finished");
            clearInterval(progressid);
            
        }
    }

});

/*
   Different functions for filtering, themeing and session handling
*/

$(window).scroll(function (e) {
    // add/remove class to navbar when scrolling to hide/show
    var scroll = $(window).scrollTop();
    if (scroll >= 270) {
        $('.navbar').addClass("navbar-hide");
    } else {
        $('.navbar').removeClass("navbar-hide");
    }
});

function filterFunction() {
    /*
    Hides all harvesters that do not match the string entered in the filter input field.
    This filter function applies to all views.
    */

    // declare variables
    var input, filter, list, card, table, divs, trs, tbody, a, i, txtValue;
    input = document.getElementById('harvesterInput');
    filter = input.value.toUpperCase();
    list = document.getElementById("div-list-view");
    card = document.getElementById("div-card-view");
    table = document.getElementById("div-table-view");

    // first: check which view is active
    // after: Loop through divs/trs and compare id names
    if (listView) {
        // get direct child divs of div-list-view
        divs = list.getElementsByClassName('harvester-list-div');
        for (i = 0; i < divs.length; i++) {
            a = divs[i];
            // divs are named {{harvester.name}}-div-list
            txtValue = a.id.split("-")[0];
            if (txtValue.toUpperCase().includes(filter)) {
                a.style.display = "";
            } else {
                a.style.display = "none";
            }
        }
    } else if (cardView) {
        // get direct child divs of div-card-view
        divs = card.getElementsByClassName('harvester-card-div');
        for (i = 0; i < divs.length; i++) {
            a = divs[i];
            // divs are named {{harvester.name}}-div-card
            txtValue = a.id.split("-")[0];
            if (txtValue.toUpperCase().includes(filter)) {
                a.style.display = "";
            } else {
                a.style.display = "none";
            }
        }
    } else if (tableView) {
        tbody = table.getElementsByTagName('tbody')[0];
        trs = tbody.getElementsByTagName('tr');
        for (i = 0; i < trs.length; i++) {
            a = trs[i];
            // trs are named {{harvester.name}}-tr-table
            txtValue = a.id.split("-")[0];
            if (txtValue.toUpperCase().includes(filter)) {
                a.style.display = "";
            } else {
                a.style.display = "none";
            }
        }
    }
}

function toggleViews() {
    /*
    Toggles between list, card and table view when page is loaded
    or a button is clicked.
    */

    // declare variables
    var listDiv, listBtn, cardDiv, cardBtn, tableDiv, tableBtn;

    // get all needed divs/buttons
    listDiv = document.getElementById("div-list-view");
    cardDiv = document.getElementById("div-card-view");
    tableDiv = document.getElementById("div-table-view");
    if (listDiv == null) return;

    listBtn = document.getElementById("btn-list-view");
    cardBtn = document.getElementById("btn-card-view");
    tableBtn = document.getElementById("btn-table-view");

    // only show active view
    listDiv.style.display = listView ? "" : "none";
    cardDiv.style.display = cardView ? "" : "none";
    tableDiv.style.display = tableView ? "" : "none";

    // only show buttons for inactive views
    if (listView) {
        addClass(listBtn, "disabled");
        removeClass(cardBtn, "disabled");
        removeClass(tableBtn, "disabled");
    } else if (cardView) {
        removeClass(listBtn, "disabled");
        addClass(cardBtn, "disabled");
        removeClass(tableBtn, "disabled");
    } else {
        removeClass(listBtn, "disabled");
        removeClass(cardBtn, "disabled");
        addClass(tableBtn, "disabled");
    }
    /*
    listBtn.style.display = listView ? "none" : "";
    cardBtn.style.display = cardView ? "none" : "";
    tableBtn.style.display = tableView ? "none" : "";
    */
}

function checkboxFunction() {
    /*
    Enables/disables links in table-view if checkboxes are checked/not checked
    and adds url with the name of the harvesters.
    */

    // declare variables
    var checkBoxes, isChecked, harvs, i, startHButton, disableHButton, tr, hname, slug;

    // check, if a checkbox is checked and get the names of the related harvesters
    checkBoxes = document.getElementsByClassName("table-view-checkbox");
    isChecked = false;
    harvs = [];
    for (i = 0; i < checkBoxes.length; i++) {
        if (checkBoxes[i].checked) {
            isChecked = true;
            // get row, where checkBox[i] is in
            tr = $(checkBoxes[i]).closest('tr');
            // trs are named {{harvester.name}}-tr-table
            hname = $(tr).attr('id').split("-")[0];
            harvs.push(hname);
        }
    }

    // concatenate all harvester names to a string for the url
    slug = '';
    for (i = 0; i < harvs.length; i++) {
        if (i < harvs.length - 1) {
            slug += harvs[i] + '-';
        } else {
            slug += harvs[i];
        }
    }

    startHButton = document.getElementById("table-checkbox-start-harvesters");
    disableHButton = document.getElementById("table-checkbox-disable-harvesters");

    // the start and disable button should only be visible, if at least one
    // checkbox is checked and the url should contain the names of the harvesters
    if (isChecked) {
        removeClass(startHButton, "disabled");
        removeClass(disableHButton, "disabled");

        $(disableHButton).attr('href', "toggle/" + slug);
        $(startHButton).attr('href', "start/" + slug);
        // note: not the best solution, might be changed later
        // to a version with dynamic url
    } else {
        addClass(startHButton, "disabled");
        addClass(disableHButton, "disabled");

        $(this).attr('href', "#");
    }
}

function checkboxMasterFunction() {
    /*
    The checkbox checks/unchecks all checkboxes in the table-view.
    */

    var masterCheckbox, checkboxes, i;
    masterCheckbox = document.getElementById("table-checkbox-master");
    checkboxes = document.getElementsByClassName("table-view-checkbox");

    for (i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = (masterCheckbox.checked) ? true : false;
    }
    checkboxFunction();
}

function checkboxShowIdle() {
    /*
    Radio button 'show idle' in the dropdown filter in table-view.
    */

    // declare variables
    var table, tbody, trs, status, hname;

    table = document.getElementById("div-table-view");
    tbody = table.getElementsByTagName('tbody')[0];
    trs = tbody.getElementsByTagName('tr');

    for (i = 0; i < trs.length; i++) {
        a = trs[i];
        hname = a.id.split("-")[0];
        status = a.getElementsByClassName("tv-status-" + hname)[0];
        if (status.innerText.includes("idle")) {
            a.style.display = "";
        } else {
            a.style.display = "none";
        }
    }
}

function checkboxHideIdle() {
    /*
    Radio button 'hide idle' in the dropdown filter in table-view.
    */

    // declare variables
    var table, tbody, trs, status, hname, i;

    table = document.getElementById("div-table-view");
    tbody = table.getElementsByTagName('tbody')[0];
    trs = tbody.getElementsByTagName('tr');

    for (i = 0; i < trs.length; i++) {
        a = trs[i];
        hname = a.id.split("-")[0];
        status = a.getElementsByClassName("tv-status-" + hname)[0];
        if (status.innerText.includes("idle")) {
            a.style.display = "none";
        } else {
            a.style.display = "";
        }
    }
}

function checkboxShowAll() {
    /*
    Radio button 'show all' in the dropdown filter in table-view.
    */

    // declare variables
    var table, tbody, trs, i;

    table = document.getElementById("div-table-view");
    tbody = table.getElementsByTagName('tbody')[0];
    trs = tbody.getElementsByTagName('tr');

    for (i = 0; i < trs.length; i++) {
        a = trs[i];
        a.style.display = "";
    }
}

//implement own add/remove class methods to avoid jquery
function hasClass(el, className) {
    if (el.classList) {
        return el.classList.contains(className);
    } else {
        return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'));
    }
}

function addClass(el, className) {
    if (el.classList) {
        el.classList.add(className);
    } else if (!hasClass(el, className)) {
        el.className += " " + className;
    }
}

function removeClass(el, className) {
    if (el.classList) {
        el.classList.remove(className);
    } else if (hasClass(el, className)) {
        var reg = new RegExp('(\\s|^)' + className + '(\\s|$)');
        el.className = el.className.replace(reg, ' ');
    }
}

function initTheme() {
    /*
    This function is called when the page is loaded to initialize the theme.
    */

    if (currentTheme === 'dark') {
        // set css if dark Theme is active in the beginning
        $('input').toggleClass("dark-input-fields");
    }
}

function getCookie(cookieName) {
    /*
    This function returns the value of the cookie
    via parameter (cookieName).
    */
    var name, decodedCookie, cookieArray, cookieEntry;

    name = cookieName + "=";
    decodedCookie = decodeURIComponent(document.cookie);
    cookieArray = decodedCookie.split(';');
    for (var i = 0; i < cookieArray.length; i++) {
        cookieEntry = cookieArray[i];

        // avoid spaces at the beginning
        while (cookieEntry.charAt(0) == ' ') {
            cookieEntry = cookieEntry.substring(1);
        }
        if (cookieEntry.indexOf(name) == 0) {
            return cookieEntry.substring(name.length, cookieEntry.length);
        }
    }
    return "";
}

function updateSession(sessionVar, value) {
    /*
    This function sends a post request to the server to change
    the session variable with the given input.
    */
    var csrftoken = getCookie('csrftoken');
    sessionData = {
        'csrfmiddlewaretoken': csrftoken,
        // computed property name: >=EcmaScript 6
        [sessionVar]: value
    };
    $.ajax({
        type: 'POST',
        url: updateSessionUrl,
        data: sessionData,
        success: function (response) {},
        error: function () {},
    });
}

function toggleTheme() {
    /*
    This function toggles between light and dark theme.
    */
    var newTheme;
    if (currentTheme === 'light') {
        // changing from light to dark Theme
        $('#toggle-theme-text').text("Light Theme");
        $('#toggle-theme-link').attr("href", "https://bootswatch.com/4/darkly/bootstrap.min.css");
        newTheme = 'dark';
    } else {
        // changing from dark to light Theme
        $('#toggle-theme-text').text("Dark Theme");
        $('#toggle-theme-link').attr("href", "https://bootswatch.com/4/materia/bootstrap.min.css");
        newTheme = 'light‚';
    }
    currentTheme = newTheme;
    $('.navbar').toggleClass("light-theme-bg dark-theme-bg");
    $('.footer').toggleClass("footer-light footer-dark");
    $('input').toggleClass("dark-input-fields");
}

function resizeFunction() {
    /*
    This function is called, when the window is resized. 
    
    For small windows the button group in table view should turn into a 
    dropdown menu and return to a button group, when the window is big again.
    (<600px: dropdown, >=600px: button group)
    */

    if ($(window).width() < 600) {
        $('.table-dropdown-btn').show();
        $('.table-btn-group').hide();
    } else {
        $('.table-dropdown-btn').hide();
        $('.table-btn-group').show();
    }
}

function getStatusHistories() {
    /*
    This function calls the server and sets the content 
    of the tooltip for the status history.
    */
    $('.status-history-button').each(function(i, obj) {
        var message;
        $.ajax({
            type: 'GET',
            url: $(this).attr("data-form"),
            context: this,
            success: function (response) {
                $(this).attr("data-original-title", response.message);
            },
            error: function () {
                message = "There has been an internal error. Please contact an administrator.";
                $(this).attr("data-original-title", message);
            },
        });
    });
}