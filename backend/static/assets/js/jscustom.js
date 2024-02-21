function validatePassword() {
    var passwordField = document.getElementById('password');
    var confirmField = document.getElementById('confirm');
    var confirmError = document.getElementById('confirmError');

    if (confirmField.value !== passwordField.value) {
        confirmError.textContent = 'Nhập lại mật khẩu không khớp';
        return false;
    } else {
        confirmError.textContent = '';
        return true;
    }
}
function validatePasswordRegister() {
    var passwordField = document.getElementById('password');
    var confirmField = document.getElementById('confirm');
    var confirmError = document.getElementById('confirmError');
    var agreementCheckbox = document.getElementById('agreement');

    if (confirmField.value !== passwordField.value) {
        confirmError.textContent = 'Nhập lại mật khẩu không khớp';
        confirmError.style.color = 'red';
        return false;
    } else if (!agreementCheckbox.checked) {
        alert("Vui lòng đồng ý với các điều khoản.");
        return false;
    } else {
        confirmError.textContent = '';
        return true;
    }
}
// Hàm hiển thị toast khi đăng nhập thành công
function showSuccessToast(message) {
    toastr.success(message, 'Success');
}
    
window.addEventListener('DOMContentLoaded', function() {
  if (window.history.replaceState) {
      window.history.replaceState(null, null, window.location.href);
  }
});
$(function () {
    var i = -1;
    var toastCount = 0;
    var $toastlast;
    var getMessage = function () {
        var msg = 'Hi, welcome to Inspinia. This is example of Toastr notification box.';
        return msg;
    };

     // Thêm toast khi đăng nhập thành công
    $('#showsimple').click(function () {
            // Display a success toast, with a title
            showSuccessToast('Without any options');
        });

    $('#showsimple').click(function (){
        // Display a success toast, with a title
        toastr.success('Without any options','Simple notification!')
    });
    $('#showtoast').click(function () {
        var shortCutFunction = $("#toastTypeGroup input:radio:checked").val();
        var msg = $('#message').val();
        var title = $('#title').val() || '';
        var $showDuration = $('#showDuration');
        var $hideDuration = $('#hideDuration');
        var $timeOut = $('#timeOut');
        var $extendedTimeOut = $('#extendedTimeOut');
        var $showEasing = $('#showEasing');
        var $hideEasing = $('#hideEasing');
        var $showMethod = $('#showMethod');
        var $hideMethod = $('#hideMethod');
        var toastIndex = toastCount++;
        toastr.options = {
            closeButton: $('#closeButton').prop('checked'),
            debug: $('#debugInfo').prop('checked'),
            progressBar: $('#progressBar').prop('checked'),
            preventDuplicates: $('#preventDuplicates').prop('checked'),
            positionClass: $('#positionGroup input:radio:checked').val() || 'toast-top-right',
            onclick: null
        };
        if ($('#addBehaviorOnToastClick').prop('checked')) {
            toastr.options.onclick = function () {
                alert('You can perform some custom action after a toast goes away');
            };
        }
        if ($showDuration.val().length) {
            toastr.options.showDuration = $showDuration.val();
        }
        if ($hideDuration.val().length) {
            toastr.options.hideDuration = $hideDuration.val();
        }
        if ($timeOut.val().length) {
            toastr.options.timeOut = $timeOut.val();
        }
        if ($extendedTimeOut.val().length) {
            toastr.options.extendedTimeOut = $extendedTimeOut.val();
        }
        if ($showEasing.val().length) {
            toastr.options.showEasing = $showEasing.val();
        }
        if ($hideEasing.val().length) {
            toastr.options.hideEasing = $hideEasing.val();
        }
        if ($showMethod.val().length) {
            toastr.options.showMethod = $showMethod.val();
        }
        if ($hideMethod.val().length) {
            toastr.options.hideMethod = $hideMethod.val();
        }
        if (!msg) {
            msg = getMessage();
        }
        $("#toastrOptions").text("Command: toastr["
                + shortCutFunction
                + "](\""
                + msg
                + (title ? "\", \"" + title : '')
                + "\")\n\ntoastr.options = "
                + JSON.stringify(toastr.options, null, 2)
        );
        var $toast = toastr[shortCutFunction](msg, title); // Wire up an event handler to a button in the toast, if it exists
        $toastlast = $toast;
        if ($toast.find('#okBtn').length) {
            $toast.delegate('#okBtn', 'click', function () {
                alert('you clicked me. i was toast #' + toastIndex + '. goodbye!');
                $toast.remove();
            });
        }
        if ($toast.find('#surpriseBtn').length) {
            $toast.delegate('#surpriseBtn', 'click', function () {
                alert('Surprise! you clicked me. i was toast #' + toastIndex + '. You could perform an action here.');
            });
        }
    });
    function getLastToast(){
        return $toastlast;
    }
    $('#clearlasttoast').click(function () {
        toastr.clear(getLastToast());
    });
    $('#cleartoasts').click(function () {
        toastr.clear();
    });
})

function showCustomToast(title, message, type) {
    var toastOptions = {
        closeButton: true,
        progressBar: true,
        showMethod: 'slideDown',
        timeOut: 4000
    };

    var toastrMessage = '<div class="custom-toast ' + type + '">' +
                            '<div class="toast-title">' + title + '</div>' +
                            '<div class="toast-message">' + message + '</div>' +
                        '</div>';

    toastr.options = toastOptions;
    toastr[type](toastrMessage, '', toastOptions);
}

  $(document).ready(function() {
      $('.footable').footable({paginate: false});

        $(".select2fillter").select2();
        $(".select2_demo_1").select2({
            placeholder: "Select a state",
            allowClear: true
        });
        $(".select2_demo_3").select2({
            placeholder: "Select a state",
            allowClear: true
        });

        $('.clockpicker').clockpicker();

        // Khởi tạo Select2 cho cả hai dropdown
        $('#select1, #select2').select2();

        // Sự kiện thay đổi của cả hai dropdown
        $('#select1, #select2').change(function () {
            var selectedValue = $(this).val();
            
            // Cập nhật giá trị của cả hai dropdown khác
            $('#select1, #select2').not(this).val(selectedValue).trigger('change.select2');
        });

    $('.dataTables-example').DataTable({
      pageLength: 25,
      responsive: true,
      ordering: false,
      dom: '<"html5buttons"B>lTfgitp',
      buttons: [
          { extend: 'copy'},
          {extend: 'csv'},
          {extend: 'excel', title: 'ExampleFile'},
          {extend: 'pdf', title: 'ExampleFile'},

          {extend: 'print',
          customize: function (win){
                  $(win.document.body).addClass('white-bg');
                  $(win.document.body).css('font-size', '10px');

                  $(win.document.body).find('table')
                          .addClass('compact')
                          .css('font-size', 'inherit');
          }
          }
      ]

  });
});


