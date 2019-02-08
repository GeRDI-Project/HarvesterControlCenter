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

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    $('#btn-deploy-harvester').on('click', function (event) {
        
        var url = '/hcc/logs';

        $.get(url, function (result) {
            var status = result;
            var data = JSON.stringify(result);
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html( data );
            $.each(status, function (hvname, element) {
                if ( element != "disabled" ) {
                    $( '#hv-status-' + hvname ).html( JSON.stringify(element) );                  
                }
            });
        }).fail(function (response) {
            $( '#form-modal' ).modal('toggle');
            $( '#form-modal-body' ).html( response.responseText );
        });
    });

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

    $('a#postharvester').on('click', function (event) {

        var url = $(this).attr("title");

        $.post(url, function (result) {
            for (var key in result) {
                alert(key + " Info: " + result[key]);
            }
        }).fail(function (response) {
            alert('Error: ' + response.responseText);
        });

    });

    $('#stopallharvesters').on('click', function (event) {

        var url = '/v1/harvesters/stop';

        $.post(url, function (result) {
            for (var key in result) {
                alert(key + " Info: " + result[key]);
            }
        }).fail(function (response) {
            alert('Error: ' + response.responseText);
        });

    });

    $('button#setcrontab').on('click', function (event) {

        var setcron = $(this).attr("title") + '/schedule?cron=' + $('input#crontab').val();
        var deletecron = $(this).attr("title") + '/schedule';

        $.ajax({
            url: deletecron,
            type: 'DELETE',
            success: function (result) {
                for (var key in result) {
                    alert(key + " Info: " + result[key]);
                }
            }
        });

        $.post(setcron, function (result) {
            for (var key in result) {
                alert(key + " Info: " + result[key]);
            }
        }).fail(function (response) {
            alert('Error: ' + response.responseText);
        });

    });

    $("div[id^='progresshv-']").load( $(this).attr("title"), function (event) {

        var url = $(this).attr("title")
        //var bar = document.getElementById("progresshv");
        var bar = this;
        var width = 99;
        var max = "";
        var id = setInterval(getTick, 1982);
    
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
    
                    $.each(data, function (index, element) {
                        $.each(element, function (i, e) {
                            if (i === 'progress_cur') {
                                width = e;
                            }
                            if (i === 'max_docs') {
                                max = e;
                            }
                        });
                    });
                });
                bar.style.width = width + '%';
                bar.innerHTML = width + '%';
    
            } else {
                bar.style.width = width + '%';
                bar.innerHTML = width + '%';
                clearInterval(id);
            }
        }
    });

});