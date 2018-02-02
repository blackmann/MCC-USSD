import requests

from api.models import Registration


def send_registration(reg):
    form_data = {
        'member_name': reg.member_name,
        'member_id': reg.member_id,
        'agent_pin': reg.agent_pin,
        'date_registered': str(reg.date_registered),
        'auth': '~ragnal~&*$^#'
    }

    res = requests.post('http://www.mysmsinbox.com/mypayutil/ndc_callback.php',
                        data=form_data)

    print(res.status_code)


def send_registrations():
    registrations = Registration.objects.all()

    last_id = 0
    for reg in registrations:
        last_id = reg.id
        send_registration(reg)

    print("Last registration was %d" % last_id)
