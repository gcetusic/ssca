$.mask.definitions['~'] = '[NSns]';
$.mask.definitions['^'] = '[EWew]';

//    text input patterns like N12 24.12, W123 20.20
var pattern_extended = '~99 99.99, ^999 99.99';
var pattern_short = '~99, ^999';

$(window).load(function () {
    var short_coord = get_short_location($('#extended').val());
    var width = $('#coordinates').css('width');
    var changed = false;
    var validated = true;

    $('#coordinates').val(short_coord);

    $('#globe').click(function () {
        alert("clicked on globe");
    });

    var location_onhover = function () {
        $(this).val($('#extended').val());
        $(this).mask(pattern_extended, {placeholder: " "});
        $(this).animate({ width: 145 }, 'slow');
    };

    var location_onblur = function () {
        if ($('#coordinates').val().length > 10) {
            if (changed)
                Dajaxice.app_public.validate_location(location_callback, {'location': $('#coordinates').val()});
            else if (validated) {
                short_coord = get_short_location($('#extended').val());
                $('#coordinates').css('border-color', '#ffffff');
                $('#globe').attr('src', '/static/images/globe_orange.png');
                $('#coordinates').animate({ width: width }, 'slow',
                    function () {
                        $('#coordinates').val(short_coord);
                        $('#coordinates').mask(pattern_short, {placeholder: " "});
                    }
                );
            }
        } else {
            short_coord = get_short_location($('#extended').val());
            $('#coordinates').css('border-color', '#ffffff');
            $('#globe').attr('src', '/static/images/globe_orange.png');
            $('#coordinates').animate({ width: width }, 'slow',
                function () {
                    $('#coordinates').val(short_coord);
                    $('#coordinates').mask(pattern_short, {placeholder: " "});
                }
            );
        }
    };

//handle server ajax response
    var location_callback = function (resp) {
        changed = false;
        $('#extended').val($('#coordinates').val());
        if (resp.status === 'error') {
            validated = false;
            $('#coordinates').css('border-color', '#ff0000');
            $('#globe').attr('src', '/static/images/globe_grey.png');
        } else {
            validated = true;
            short_coord = get_short_location($('#extended').val());
            $('#coordinates').css('border-color', '#ffffff');
            $('#globe').attr('src', '/static/images/globe_orange.png');
            $('#coordinates').animate({ width: width }, 'slow',
                function () {
                    $('#coordinates').val(short_coord);
                    $('#coordinates').mask(pattern_short, {placeholder: " "});
                }
            );
        }
    };

    var location_onenter = function (event) {
        changed = true;
        if (event.which == 13) {
            $(this).blur();
        }
    };

    $('#coordinates').focus(location_onhover).blur(location_onblur)
        .keypress(location_onenter);

});

// return short form of location
function get_short_location(extended) {
    pattern_short = '~99, ^999';
    var splited = extended.split(' ');
    if (splited[2][1] === '0') {
        splited[2] = splited[2][0] + splited[2][2] + splited[2][3];
        pattern_short = '~99, ^99';
    }
    return splited[0] + ' ' + splited[2];
}

