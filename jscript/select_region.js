function selectRegion(){
                var id_region = $('select[name="region"]').val();
                if(!id_region){
                        $('div[name="selectDataRegion"]').html('');
                }
                else {
                    $.ajax({
                        type: "GET",
                        url: "../region_selector",
                        data: {'id_region': id_region},
                        dataType: "json",
                        success: function(city_list) {
                            var html = '';
                            $.each(city_list, function (i, d){
                                html += '<option value="' + d + '">' + d + '</option>';
                            });
                            $("#city").html(html);
                        }
                    });
                };
        };


function EmailCheck(val) {
    var re = /^[\w-\.]+@[\w-]+\.[a-z]{2,4}$/i;
    var valid = re.test(val);

    if (valid) output = 'black';
        else output = 'red';

    document.getElementById('email').style.color = output;
    }

function PhoneCheck(val) {
    var re = /^\d[\d\(\)\ -]{4,14}\d$/;
    var valid = re.test(val);
    if (valid) output = 'black';
        else output = 'red';

    document.getElementById('phone').style.color = output;
    }


function SubmitCorrectData()
    {
    var phone_col = document.getElementById('phone').style.color;
    var email_col = document.getElementById('email').style.color;

    if ((phone_col == 'black' && email_col =='black')) return true;
        else
        {
            alert("Данные телефона или почты неверно введены. Проверьте правильность ввода.");
            return false;
        }
    }