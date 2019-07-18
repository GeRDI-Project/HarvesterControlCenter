/*
Copyright © 2017 Jan Frömberg (http://www.gerdi-project.de)

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

/*
   Execute when DOM is ready
*/
$(function () {

    $('#loaderSpinnerLog').hide();
    $('#loaderSpinnerStat').hide();

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

    $('#div-list-view').hide();
    $('#div-table-view').hide();
    $('#btn-card-view').hide();
    
    $('#btn-harvester-log').on('click', function (event) {
    load_into_modal(this);
    });

    $('#btn-hcc-log').on('click', function (event) {
        load_into_modal(this);
    });

    $('#btn-list-view').click(function () {
        $('#div-card-view').hide();
        $('#div-table-view').hide();
        $('#div-list-view').show();

        $('#btn-list-view').hide();
        $('#btn-card-view').show();
        $('#btn-table-view').show();
    });

    $('#btn-card-view').click(function () {
        $('#div-list-view').hide();
        $('#div-table-view').hide();
        $('#div-card-view').show();

        $('#btn-card-view').hide();
        $('#btn-list-view').show();
        $('#btn-table-view').show();
    });

    $('#btn-table-view').click(function () {
        $('#div-card-view').hide();
        $('#div-list-view').hide();
        $('#div-table-view').show();

        $('#btn-table-view').hide();
        $('#btn-card-view').show();
        $('#btn-list-view').show();
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

    $(".harvesterconfig").click(function (ev) { // for each edit harvester url
        ev.preventDefault(); // prevent navigation
        var url = $(this).attr("data-form"); // get the harvester form url
        $("#config-modal").load(url, function () { // load the url into the modal
            $(this).modal('show'); // display the modal on url load
        });
        return false; // prevent the click propagation
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
                $('#message-modal-header').text(response.status=='Ok' ? 'Success!' : 'Error');
                $('#message-modal-body').text(response.message);
                $('#message-modal').modal('show');
            },
            error: function (response){
                $('#message-modal-header').text('Error!');
                $('#message-modal-body').text('There has been an internal error. Please contact an administrator.');
                $('#message-modal').modal('show');
            },
        });
        return false;
    });

    $('#table-checkbox-disable-harvesters').click(function(){
        if($(this).hasClass("active")){
            $('#message-modal-header').text('Work in progress');
            $('#message-modal-body').text('Nothing to see here...');
            $('#message-modal').modal('show');
        }    
    });

    $('#table-checkbox-start-harvesters').click(function(){
        if($(this).hasClass("active")){
            $('#message-modal-header').text('Work in progress');
            $('#message-modal-body').text('Nothing to see here...');
            $('#message-modal').modal('show');
        }    
    });
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

    // Declare variables
    var input, filter,list, card, table, divs, trs, tbody, a, i, txtValue;
    input = document.getElementById('harvesterInput');
    filter = input.value.toUpperCase();
    list = document.getElementById("div-list-view");
    card = document.getElementById("div-card-view");
    table = document.getElementById("div-table-view");

    // first: check which div is visible (same implementation like jQuerys :visible)
    // after: Loop through divs/trs and compare id names
    if (list.offsetWidth > 0 && list.offsetHeight > 0){
        divs = list.getElementsByClassName('harvester-list-div');//direct child divs of div-list-view
        for (i=0; i<divs.length; i++){
            a = divs[i];
            txtValue = a.id.split("-")[0]; //divs are named {{harvester.name}}-div-list
            if(txtValue.toUpperCase().includes(filter)){
                a.style.display = "";
            } else {
                a.style.display = "none";
            }
        }
    } else if (card.offsetWidth > 0 && card.offsetHeight > 0){
        divs = card.getElementsByClassName('harvester-card-div');//direct child divs of div-card-view
        for (i=0; i<divs.length; i++){
            a = divs[i];
            txtValue = a.id.split("-")[0]; //divs are named {{harvester.name}}-div-card
            if(txtValue.toUpperCase().includes(filter)){
                a.style.display = "";
            } else {
                a.style.display = "none";
            }
        }
    } else if (table.offsetWidth > 0 && table.offsetHeight > 0){
        tbody = table.getElementsByTagName('tbody')[0];//only tbody changes, thead should always be visible
        trs = tbody.getElementsByTagName('tr');
        for (i=0; i<trs.length; i++){
            a = trs[i];
            txtValue = a.id.split("-")[0]; //trs are named {{harvester.name}}-tr-table
            if(txtValue.toUpperCase().includes(filter)){
                a.style.display = "";
            } else {
                a.style.display = "none";
            }
        }
    }
}

function checkboxFunction(){
    //enables/disables buttons in table-view if checkboxes are checked/not checked

    var checkBoxes, isChecked, i, startHButton, disableHButton;
    checkBoxes = document.getElementsByClassName("table-view-checkbox");
    isChecked = false;
    for (i=0; i<checkBoxes.length; i++){
        if (checkBoxes[i].checked){
            isChecked = true;
        }
    }
    startHButton = document.getElementById("table-checkbox-start-harvesters");
    disableHButton = document.getElementById("table-checkbox-disable-harvesters");
    if(isChecked){
        removeClass(startHButton, "disabled");
        addClass(startHButton, "active");

        removeClass(disableHButton, "disabled");
        addClass(disableHButton, "active");
    }else{
        removeClass(startHButton, "active");
        addClass(startHButton, "disabled");

        removeClass(disableHButton, "active");
        addClass(disableHButton, "disabled");
    }
}
//implement own add/remove class methods to avoid jquery
function hasClass(el, className) {
    if (el.classList)
      return el.classList.contains(className)
    else
      return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'))
}
  
function addClass(el, className) {
    if (el.classList)
        el.classList.add(className)
    else if (!hasClass(el, className)) el.className += " " + className
}
  
function removeClass(el, className) {
    if (el.classList)
        el.classList.remove(className)
    else if (hasClass(el, className)) {
        var reg = new RegExp('(\\s|^)' + className + '(\\s|$)')
        el.className=el.className.replace(reg, ' ')
    }
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

// good coding examples for non anonymous functions
var formButton = {
    regClick: function () {
        $('#form-modal-body').load('/hcc/register #hreg-form-content', formButton.toggleModal);
    },

    toggleModal: function () {
        $('#form-modal').modal('toggle');
        formAjaxSubmit.init('#form-modal-body form', '#form-modal');
    }
};

var formAjaxSubmit = {
    init: function (form, modal) {
        $(form).submit(formAjaxSubmit.ajax);
    },

    ajax: function (e) {
        e.preventDefault();
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: formAjaxSubmit.succFunc,
            error: formAjaxSubmit.errorFunc,
        });
    },

    succFunc: function (xhr, ajaxOptions, thrownError) {
        if ($(xhr).find('.has-error').length > 0) {
            $(modal).find('.modal-body').html(xhr);
            formAjaxSubmit.init(form, modal);
        } else {
            $(modal).modal('toggle');
        }
    },

    errorFunc: function (xhr, ajaxOptions, thrownError) {
        // handle response errors here
    }
};

$('#register-button').click(formButton.regClick);