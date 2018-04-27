$( document ).ready( function(){

  $('#register-button').click( formButton.regClick );

  var formAjaxSubmit = {
      init : function(form, modal) {
        $(form).submit( formAjaxSubmit.ajax );
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
         if ( $(xhr).find('.has-error').length > 0 ) {
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

  var formButton = {
    regClick: function() {
        $('#form-modal-body').load('/v1/harvesters/register #hreg-form-content', formButton.toggleModal);
    },

    toggleModal: function () {
        $('#form-modal').modal('toggle');
        formAjaxSubmit.init('#form-modal-body form', '#form-modal');
    }
  };
});
