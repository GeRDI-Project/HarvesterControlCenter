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

$(document).ready(function () {
    
    $('.loaderImage').hide();
    $('.loaderImageLog').hide();
    var ctx = document.getElementById("harvesterChart");
    var myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['new_label'],
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

    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });

    $('#btn-deploy-harvester').on('click', function (event) {
        
        var url = $(this).attr("title");
        $('.loaderImageLog').show();
        $.get(url, function (result) {
            var status = result;
            var data = JSON.stringify(result);
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html( data );
            for (var key in status) {
                var obj = status[key];
                $( '#hv-status-' + key ).html( obj.log );
            }
            $('.loaderImageLog').hide();
        
        }).fail(function (response) {
            $('.loaderImageLog').hide();
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html( response.responseText );
        });
    });

    $('#collapseChart').on('show.bs.collapse', function (event) {
        
        var url = $(this).attr("title");
        $('.loaderImage').show();
        $.get(url, function (result) {
            
            updateGUI(result);
        
        }).fail(function (response) {

            $('.loaderImage').hide();
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html( response.responseText );
            
        });
    });

    function updateChart(labels, data, bgColorArray, bColorArray) {

        $('.loaderImage').hide();

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
                    $( '#progresshv-' + key ).show();
                } else {
                    $( '#progresshv-' + key ).hide();
                }
                if ( obj.data_pvd ) {
                    $( '#btn-harvester-status-' + key ).prop('title', obj.data_pvd + ': ' + obj.cached_docs + ' of ' + obj.max_docs + '. ' + obj.lastHarvestDate);
                }
            }
        }

        updateChart(vlabels, vdata, gbcarray, bcarray);
    }

    var formButton = {
        regClick: function () {
            $('#form-modal-body').load('/v1/harvesters/register #hreg-form-content', formButton.toggleModal);
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

    // milisec to hours, min, sec
    function timeConvert(n) {
        var milisec = n;
        var rseconds = Math.floor( (milisec / 1000) % 60 );
        var rminutes = Math.floor( (milisec / (1000*60)) % 60 );
        var rhours   = Math.round( (milisec / (1000*60*60)) % 24 );
        return rhours + "h " + rminutes + "min " + rseconds + "sec";
    }

    $("div[id^='progresshv-']").load( $(this).attr("title"), function (event) {

        var url = $(this).attr("title");
        var bar = this;
        var width = 99;
        var perc = "%";
        var max = "";
        var harvester_name = "";
        var id = setInterval(getTick, 1982);
        var remain;
        var time = 0;
        var time_string = "";
    
        function getTick() {
            
            if (!(width >= 100 || width === 'undefined') || max === 'N/A') {
                var request = $.ajax({
                    url: url,
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
                        harvester_name = key;
                        width = data[key].progress_cur;
                        remain = data[key].remainingHarvestTime;
                        max = data[key].max_docs;                        
                    }
                });

                bar.style.width = width + "%";
                if ( max === "N/A" ) {
                    perc = "";
                }
                if ( typeof remain !== "undefined" ) {
                    time = timeConvert(remain);
                    time_string = 'remaining time: ' + time;
                }
                $( '#status-label-' + harvester_name).html( time_string );
                bar.innerHTML = width + perc;
    
            } else {
                bar.style.width = width + '%';
                bar.innerHTML = width + '%';
                $( '#status-label-' + harvester_name).html( "" );
                clearInterval(id);
            }
        }
    });

});