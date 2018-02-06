import requests

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
    return ["mtn", "airtel", "tigo"][int(position) - 1]


def pay(mobile_number, amount, ussd_number, network, id_type, id_number, intent):
    response = requests.post("https://payment.mypayutil.com/api/users/authenticate",
                             data={"mobileNumber": "0000000006",
                                   "password": "memberReg#Newdeveloper5"})

    print("[Request Payment] Authenticating...")
    if str(response.status_code).startswith("20"):
        print("Authentication done, success")
        json_response = response.json()
        access_token = json_response['access_token']

        request_body = {
            "mobileNumber": mobile_number,
            "source": "USSD",
            "thirdPartyRef": "N/A",
            "amount": amount,
            "parameters": {
                "ID Type": id_type,
                "ID Number": id_number,
                "Intent": intent,
                "USSD Number": ussd_number,
            },
            "service": "5a12c32e2adb093f1c8bf0f4"
        }

        print(request_body)
        print(network)

        headers = {
            "Authorization": "Bearer %s" % access_token
        }

        res = requests.post("https://payment.mypayutil.com/api/merchants/payments/%s" % network,
                            json=request_body,
                            headers=headers)

        print("Request made %d %s" % (res.status_code, res.text,))

    else:
        print("Failed %d" % response.status_code)


def request_payment(mobile_number, amount, ussd_number, network, id_type, id_number, intent):
    import threading

    thread = threading.Thread(target=pay, args=(mobile_number, amount, ussd_number, network, id_type, id_number, intent))
    thread.daemon = True
    thread.start()
