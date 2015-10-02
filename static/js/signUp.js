$(function() {
    $('#btnSignUp').click(function() {
 
        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                var data = JSON.parse(response);
                if (parseInt(data.success)) window.location.href = "/showSignin";
                else alert(data.error);
            },
            error: function(error) {
                alert("there was an error: " + error);
            }
        });
    });
});