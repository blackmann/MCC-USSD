import requests
from requests.auth import HTTPBasicAuth

# Notes
# ClientState is structured in the form 'branching_method':'current_level' then other data
# follow -> 1:2:Degreat Yartey:Alogboshie:1:etc
# this is used to determine which level the user has gotten to and what to show

RELEASE_USSD = "Release"
RESPONSE_USSD = "Response"

CLIENT_STATE = "ClientState"
MESSAGE = "Message"

INITIAL_CLIENT_STATE = "1"

OPTION_PAY_DUES_ORDINARY = "1"
# OPTION_PAY_DUES_EXECUTIVE = "2"
OPTION_REGISTER_MEMBER = "2"

BRANCH_A = "a"
BRANCH_B = "b"

invalid_option_data = {
    "Type": RELEASE_USSD,
    "Message": "The option you selected is not valid. Please try again!"
}


def get_network(position):
    return ["mtn-gh", "airtel-gh", "vodafone-gh"][int(position) - 1]


def pay(mobile_number, amount, ussd_number, network, id_type, id_number, intent, token=None):
    callback_url = "https://mcc-ussd-1.herokuapp.com/%s/%s/%s/%s/%s/%s/" % (
        mobile_number, ussd_number, intent.replace(
            " ", "-"), id_type.replace(" ", "-"), id_number.replace(" ", "-"), network
    )

    data = {
        "CustomerName": "Member:%s" % id_number,
        "CustomerMsisdn": mobile_number,
        "Channel": network,
        "Amount": amount,
        "FeesOnCustomer": False,
        "PrimaryCallbackUrl": callback_url,
        "Description": intent,
        "Token": token
    }

    auth_header = HTTPBasicAuth("fhojqavg", "rgbekrne")

    r = requests.post("https://api.hubtel.com/v1/merchantaccount/merchants/HM0805180003/receive/mobilemoney",
                      json=data, auth=auth_header)

    print("Response from hubtel %s" % str(r.status_code))


def request_payment(mobile_number, amount, ussd_number, network, id_type, id_number, intent, token=None):
    import threading

    thread = threading.Thread(target=pay, args=(
        mobile_number, amount, ussd_number, network, id_type, id_number, intent, token))
    thread.daemon = True
    thread.start()


def spd(data):
    res = requests.post('http://www.mysmsinbox.com/mypayutil/ndc_callback.php',
                  files=data)
    print("Response from mcc is %s" % res.status_code)


def send_payment_data(data):
    import threading

    thread = threading.Thread(target=spd, args=(data, ))
    thread.daemon = True
    thread.start()
