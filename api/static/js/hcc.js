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
$( function () {
    
    $('#loaderSpinnerLog').hide();
    $('#loaderSpinnerStat').hide();

    var ctx = document.getElementById("harvesterChart");
    if ( ctx != null ) {
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
            options: { cutoutPercentage: 45 }
        });
    }
    
    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });

    $('#btn-deploy-harvester').on('click', function (event) {
        load_into_modal(this);
    });

    $('#btn-hcc-log').on('click', function (event) {
        load_into_modal(this);
    });

    function load_into_modal (_this) {
        var url = $(_this).attr("title");
        $('#loaderSpinnerLog').show();
        $.get(url, function (result) {
            var status = result;
            var data = JSON.stringify(result, undefined, 2);
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html('<pre>' + data + '</pre>');
            for (var key in status) {
                var obj = status[key];
                $( '#hv-status-' + key ).html( obj.log );
            }
            $('#loaderSpinnerLog').hide();
        
        }).fail(function (response) {
            $( '#loaderSpinnerLog' ).hide();
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html( response.responseText );
        });
    }

    $('#collapseChart').on('show.bs.collapse', function (event) {
        
        var url = $(this).attr("title");
        $('#loaderSpinnerStat').show();
        $.get(url, function (result) {
            
            updateGUI(result);
        
        }).fail(function (response) {

            $('#loaderSpinnerStat').hide();
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html( response.responseText );
            
        });
    });

    function updateChart(labels, data, bgColorArray, bColorArray) {

        $('#loaderSpinnerStat').hide();

        myChart.data.labels.pop();
        myChart.data.datasets.forEach( function(dataset) {
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
            if ( obj != 'disabled' ) {
                
                $( '#hv-status-' + key ).html( JSON.stringify(obj) );
                var btnhvstatus = document.getElementById('btn-harvester-status-' + key);
                if ( btnhvstatus ) {
                    btnhvstatus.classList.toggle("btn-info", false);
                    btnhvstatus.classList.toggle("btn-warning", false);
                    btnhvstatus.classList.toggle("btn-success", false);
                    btnhvstatus.classList.add( "btn-" + obj.gui_status );
                }
                if ( obj.status ) {
                    var lbl_status = document.getElementById('lbl-harvester-status-' + key);
                    lbl_status.innerHTML = obj.status ;
                }
                if ( obj.cached_docs ) {
                    vlabels.push( key );
                    vdata.push( parseInt(obj.cached_docs) );
                    var r = (Math.floor(Math.random() * 256));
                    var g = (Math.floor(Math.random() * 256));
                    var b = (Math.floor(Math.random() * 256));
                    gbcarray.push( 'rgba(' + r + ',' + g + ',' + b + ',0.3)' );
                    bcarray.push( 'rgba(' + r + ',' + g + ',' + b + ',0.4)' );
                }
                if ( obj.health != 'OK' ) {
                    $( '#health-exclamation-' + key ).show();
                    $( '#health-exclamation-' + key ).prop('title', obj.health );
                } else {
                    $( '#health-exclamation-' + key ).hide();
                }
                if ( obj.status == 'harvesting' ) {
                    //$( '#progresshv-' + key ).show();
                } else {
                    //$( '#progresshv-' + key ).hide();
                }
                if ( obj.data_pvd ) {
                    $( '#btn-harvester-status-' + key ).attr('data-original-title', obj.data_pvd + 
                    ' harvested and cached documents: ' + 
                    obj.cached_docs + ' of ' + 
                    obj.max_docs + '. Last harvest: ' + 
                    obj.lastHarvestDate);
                }
            }
        }

        updateChart(vlabels, vdata, gbcarray, bcarray);
    }

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

});

/*
    Execute when Page/window is loaded
*/
$( window ).ready( function(){

    // milisec to hours, min, sec
    var timeConvert = function (milis) {
        var milisec = milis;
        var rseconds = Math.floor( (milisec / 1000) % 60 );
        var rminutes = Math.floor( (milisec / (1000*60)) % 60 );
        var rhours   = Math.round( (milisec / (1000*60*60)) % 24 );
        return rhours + "h " + rminutes + "min " + rseconds + "sec";
    };

    var lbl_status = document.querySelectorAll('*[id^="lbl-harvester-status-"]');
    var lblarray = Array.from(lbl_status);
    if ( lblarray.length > 0 ) {
        for (var key in lblarray) {

            var obj = lblarray[key];
            var objid = obj.id;
            var me = objid.split('-')[3];

            if ( obj.innerText == 'harvesting' || obj.innerText == 'queued' ) { 
        
                var is = $( '#progresshv-' + me);
                is.addClass( "progress-bar-animated" );
                is.removeClass ( "progress-bar-grey" );
                var remember = is.attr("title");
                var intervalid = setInterval( getProgress, 1982, remember, me );
            }
        }
    }

    function getProgress(_url, _harv) {
        
        var bar = $( '#progresshv-' + _harv);
        var timelabel = $( '#status-label-' + _harv);
        var statuslabel = $( '#lbl-harvester-status-' + _harv);
        var width = parseInt(bar[0].innerText.replace('%', ''));
        var state = statuslabel[0].innerText;
        var perc = "%";
        var remain;
        var time = 0;
        var time_string = "";

        if ( state == 'harvesting' || state == 'queued' || typeof state == "undefined" ) {

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
                for ( var key in data ) {

                    width = data[key].progress_cur;
                    remain = data[key].remainingHarvestTime;
                    max = data[key].max_docs;
                    cache = data[key].progress;
                    state = data[key].state;

                    $( '#btn-harvester-status-' + key ).attr('data-original-title',
                    cache + ' of ' + max);
                    statuslabel.html(state);

                    // referenced by context, this
                    bar.css("width", width + "%");
                    if ( max === "N/A" ) {
                        perc = "";
                    }
                    if ( typeof remain !== "undefined" ) {
                        time = timeConvert(remain);
                        time_string = 'remaining time: ' + time;
                    }
                    timelabel.html( time_string );
                    bar.html(width + perc);
                }
            });

        } else {

            bar.removeClass( "progress-bar-animated" );
            bar.addClass( "progress-bar-grey" );
            bar.css("width", width + "%");
            bar.html(width + '%');
            timelabel.html( "" );
            statuslabel.html("finished");
            clearInterval(intervalid);

        }
    }

});

function filterFunction() {

    // Declare variables
    var input, filter, list, btns, a, i, txtValue;
    input = document.getElementById('harvesterInput');
    filter = input.value.toUpperCase();
    list = document.getElementById("harvesterList");
    btns = list.getElementsByTagName('button');
  
    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < btns.length; i++) {
      a = btns[i];
      txtValue = a.textContent || a.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        btns[i].parentElement.parentElement.parentElement.parentElement.style.display = "";
      } else {
        btns[i].parentElement.parentElement.parentElement.parentElement.style.display = "none";
      }
    }
}

$( window ).scroll(function(e) {

    // add/remove class to navbar when scrolling to hide/show
    var scroll = $(window).scrollTop();
    if (scroll >= 150) {
        $('.navbar').addClass("navbar-hide");
    } else {
        $('.navbar').removeClass("navbar-hide");
    }

});