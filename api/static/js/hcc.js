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

var listView, cardView, tableView;
// which view is shown at the moment (especially at the beginning)
listView = false;
tableView = false;
cardView = true;

/*
   Execute when DOM is ready
*/
$(function () {

    $('#loaderSpinnerLog').hide();
    $('#loaderSpinnerStat').hide();

    toggleViews();

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
        $.get(url, function (result) {
            var status = result;
            var data = JSON.stringify(result, undefined, 2);
            $('#form-modal').modal('toggle');
            $('#form-modal-body').html('<pre>' + data + '</pre>');
            for (var key in status) {
                var obj = status[key];
                $('#hv-status-' + key).html(obj.log);
            }
            $('#loaderSpinnerLog').hide();

        }).fail(function (response) {
            $('#loaderSpinnerLog').hide();
            $('#form-modal').modal('toggle');
            $('#form-modal-body').html(response.responseText);
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

    /*
        Buttons
    */

    $('#btn-harvester-log').on('click', function (event) {
        load_into_modal(this);
    });

    $('#btn-hcc-log').on('click', function (event) {
        load_into_modal(this);
    });

    $('#btn-list-view').click(function () {
        listView = true;
        cardView = false;
        tableView = false;
        toggleViews();
        filterFunction();
    });

    $('#btn-card-view').click(function () {
        listView = false;
        cardView = true;
        tableView = false;
        toggleViews();
        filterFunction();
    });

    $('#btn-table-view').click(function () {
        listView = false;
        cardView = false;
        tableView = true;
        toggleViews();
        filterFunction();
    });

    $('#collapseChart').on('show.bs.collapse', function (event) {

        var url = $(this).attr("title");
        $('#loaderSpinnerStat').show();
        $.get(url, function (result) {

            updateGUI(result);

        }).fail(function (response) {

            $('#loaderSpinnerStat').hide();
            $('#form-modal').modal('toggle');
            $('#form-modal-body').html(response.responseText);

        });
    });

    $(".harvesteredit").click(function (ev) { // for each edit harvester url
        ev.preventDefault(); // prevent navigation
        var url = $(this).attr("data-form"); // get the harvester form url
        $("#harvesterModal").load(url, function () { // load the url into the modal
            $(this).modal('show'); // display the modal on url load
        });
        return false; // prevent the click propagation
    });

    $(".harvesterconfig").click(function (ev) {
        ev.preventDefault();
        var url = $(this).attr("data-form");
        $("#config-modal").load(url, function () {
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
                $('#message-modal').modal('show');
            },
            error: function (response) {
                $('#message-modal-header').text('Error!');
                $('#message-modal-body').text('There has been an internal error. Please contact an administrator.');
                $('#message-modal').modal('show');
            },
        });
        return false;
    });

    $('.status-radio').click(function () {
        /*
        Related to the radio buttons in drodown menu in table-view
        */
        if ($('#checkbox-show-all').prop('checked')) checkboxShowAll();
        if ($('#checkbox-show-idle').prop('checked')) checkboxShowIdle();
        if ($('#checkbox-hide-idle').prop('checked')) checkboxHideIdle();
    });

    $('#btn-load-harvester-data').click(function(ev) {
        ev.preventDefault();
        $('#file-upload-modal input').val('');
        $('input[name=csrfmiddlewaretoken]').attr('value', getCookie("csrftoken"));
        $('#file-upload-modal').modal("show");
        return false;
    });
    /*
    $('#upload-file-form').submit(function(ev) {
        ev.preventDefault();
        var serializedData = new FormData($(this));
        console.log(serializedData)
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: serializedData,
            context: this,
            success: function(response){
                $('#file-upload-modal').modal('hide');
                $('#message-modal-header').text('Success!');
                $('#message-modal-body').text(response.message);
                $('#message-modal').modal('show');
            },  
            error: function (response) {
                $('#file-upload-modal').modal('hide');
                $('#message-modal-header').text('Error!');
                $('#message-modal-body').text('There has been an internal error. Please contact an administrator.');
                $('#message-modal').modal('show');
            },    
        });
        return false;
    });
    */
});

/*
    Execute when page/window is loaded
*/
$(window).ready(function () {

    // milisec to hours, min, sec
    var timeConvert = function (milis) {
        var milisec = milis;
        var rseconds = Math.floor((milisec / 1000) % 60);
        var rminutes = Math.floor((milisec / (1000 * 60)) % 60);
        var rhours = Math.round((milisec / (1000 * 60 * 60)) % 24);
        return rhours + "h " + rminutes + "min " + rseconds + "sec";
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
                var intervalid = setInterval(getProgress, 1982, remember, me);
            }
        }
    }

    function getProgress(_url, _harv) {

        var bar = $('#progresshv-' + _harv);
        var timelabel = $('#status-label-' + _harv);
        var statuslabel = $('#lbl-harvester-status-' + _harv);
        var width = parseInt(bar[0].innerText.replace('%', ''));
        var state = statuslabel[0].innerText;
        var perc = "%";
        var remain;
        var time = 0;
        var time_string = "";

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
                    max = data[key].max_docs;
                    cache = data[key].progress;
                    state = data[key].state;

                    $('#btn-harvester-status-' + key).attr('data-original-title',
                        cache + ' of ' + max);
                    statuslabel.html(state);

                    // referenced by context, this
                    bar.css("width", width + "%");
                    if (max === "N/A") {
                        perc = "";
                    }
                    if (typeof remain !== "undefined") {
                        time = timeConvert(remain);
                        time_string = 'remaining time: ' + time;
                    }
                    timelabel.html(time_string);
                    bar.html(width + perc);
                }
            });

        } else {

            bar.removeClass("progress-bar-animated");
            bar.addClass("progress-bar-grey");
            bar.css("width", width + "%");
            bar.html(width + '%');
            timelabel.html("");
            statuslabel.html("finished");
            clearInterval(intervalid);

        }
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
    or a button is clicked
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
    listBtn.style.display = listView ? "none" : "";
    cardBtn.style.display = cardView ? "none" : "";
    tableBtn.style.display = tableView ? "none" : "";
}

function checkboxFunction() {
    /*
    Enables/disables links in table-view if checkboxes are checked/not checked
    and adds url with the name of the harvesters
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
    The checkbox checks/unchecks all checkboxes in the table-view
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
    Radio button 'show idle' in the dropdown filter in table-view
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
        if (status.innerText == "idle") {
            a.style.display = "";
        } else {
            a.style.display = "none";
        }
    }
}

function checkboxHideIdle() {
    /*
    Radio button 'hide idle' in the dropdown filter in table-view
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
        if (status.innerText == "idle") {
            a.style.display = "none";
        } else {
            a.style.display = "";
        }
    }
}

function checkboxShowAll() {
    /*
    Radio button 'show all' in the dropdown filter in table-view
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

function getCookie(cookieName) {
    var name, decodedCookie, cookieArray, c;

    name = cookieName + "=";
    decodedCookie = decodeURIComponent(document.cookie);
    cookieArray = decodedCookie.split(';');
    for(var i = 0; i < cookieArray.length; i++) {
        c = cookieArray[i];

        // avoid spaces at the beginning
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

$(window).scroll(function (e) {
    // add/remove class to navbar when scrolling to hide/show
    var scroll = $(window).scrollTop();
    if (scroll >= 270) {
        $('.navbar').addClass("navbar-hide");
    } else {
        $('.navbar').removeClass("navbar-hide");
    }
});

function toggleTheme() {
    if ($('#toggle-mode-text').text() == "Dark Mode") {
        // changing from light to dark mode
        $('#toggle-mode-text').text("Light Mode");
        $('#toggle-mode-link').attr("href", "https://bootswatch.com/4/darkly/bootstrap.min.css");
    } else {
        // changing from dark to light mode
        $('#toggle-mode-text').text("Dark Mode");
        $('#toggle-mode-link').attr("href", "https://bootswatch.com/4/materia/bootstrap.min.css");
    }

    $('.navbar').toggleClass("light-mode-bg dark-mode-bg");
    $('.footer').toggleClass("footer-light footer-dark");
    $('input').toggleClass("dark-input-fields");
}