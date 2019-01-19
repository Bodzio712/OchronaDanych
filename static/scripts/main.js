window.onload = function() {
    add_navbar();
}

    function add_navbar(){
         $.ajax({
        type: "GET",
        url: "http://127.0.0.1:5000/isLogged",
        dataType: "json",
        contentType:"application/json",
        success: function(response) {
            var $nv = $('#log');
            var data = JSON.parse(response);
            for(i in data) {
                var is_logged = data[i];
                if(is_logged == "false"){
                    $nv.append('<a class="nav-link" href="/login">Zaloguj</a>\n')
                }
                else {
                    $nv.append('<a class="nav-link" href="/logout">Wyloguj</a>\n')
                }
            }
        }
        })
    }


// Funkcja walidująca poprawnosć wpisanych danych do formularza rejestracji
function validate() {
    var error_messege = "";

    if(validate_is_passwords_are_the_same() == false)
        error_messege +="Wprowadzona hasła nie są jednakowe\n";

    if (chceck_password_lenght() == false)
        error_messege += "Hasło powinno składać sie z co najmniej 8 znaków\n";



    if(error_messege.length > 2) {
        alert(error_messege);
        return false;
    }
    else
        return true;
}

//Sprawdzanier czy hasła są takie same
function validate_is_passwords_are_the_same(){
    var password = document.getElementById("password").value;
    var rpassword = document.getElementById("rpassword").value;

    if(password == rpassword)
        return true;
    else
        return false;
}

//Sprawdzanie czy hasło jest wystarczająco długie
function chceck_password_lenght() {
    var password = document.getElementById("password").value;

    if(password.length < 8)
        return false;
    else
        return true;
}