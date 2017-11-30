import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
OPTION_PAY_DUES_EXECUTIVE = "2"
OPTION_REGISTER_MEMBER = "3"

invalid_option_data = {
    "Type": RELEASE_USSD,
    "Message": "The option you selected is not valid. Please try again!"
}


def check_validity(mobile_number):
    return False


def get_network(position):
    return ["mtn", "airtel", "tigo"][int(position) - 1]


def request_payment(mobile_number, amount, ussd_number, network, id_type, id_number, intent):
    response = requests.post("https://payment.mypayutil.com/api/users/authenticate",
                             data={"mobileNumber": "0000000006",
                                   "password": "memberReg#Newdeveloper5"})

    print("[Request Payment] Authenticating...")
    if str(response.status_code).startswith("20"):
        print("Authentication done, success")
        json_response = response.json()
        access_token = json_response['access_token']

        actual_id = ["Voters", "Membership"][int(id_type) - 1]

        request_body = {
            "mobileNumber": mobile_number,
            "source": "USSD",
            "thirdPartyRef": "N/A",
            "amount": amount,
            "parameters": {
                "ID Type": actual_id,
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


def handle_registration(request, level):
    state_branch = 2
    next_level = int(level) + 1

    # the person has provided constituency
    if level == 1:
        return {
            "Message": "Please select a ID type.\n\n1. Voter's ID\n2. Membership ID",
            "ClientState": "%d:%d" % (state_branch, next_level,),
            "Type": RESPONSE_USSD
        }

    if level == 2:
        user_id_type = request.data.get(MESSAGE)

        return {
            "Message": "Please enter your ID Number",
            "ClientState": "%d:%d:%s" % (state_branch, next_level, user_id_type),
            "Type": RESPONSE_USSD
        }

    if level == 3:
        user_id = request.data.get(MESSAGE)
        user_id_type = request.data.get(CLIENT_STATE).split(":")[2]

        valid = check_validity(request.data.get("Mobile"))
        if valid:
            return {
                "Message": "You have been registered to receive updates already.",
                "Type": RELEASE_USSD
            }

        else:
            return {
                "Message": "Please select a payment method to pay registration fee of GHS 3.00\n\n1. MTN Mobile "
                           "Money\n2. Airtel Money",
                "ClientState": "%d:%d:%s:%s" % (state_branch, next_level, user_id_type, user_id),
                "Type": RESPONSE_USSD
            }

    if level == 4:
        payment_option = request.data.get(MESSAGE)
        if not (payment_option in [str(a) for a in range(1, 3)]):
            return invalid_option_data

        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        return {
            "Message": "Please enter your mobile money phone number",
            "ClientState": "%d:%d:%s:%s:%s" % (state_branch, next_level, id_type, user_id, payment_option),
            "Type": RESPONSE_USSD
        }

    if level == 5:
        mobile_number = request.data.get(MESSAGE)
        if len(mobile_number) != 10:
            return invalid_option_data

        payment_option = request.data.get(CLIENT_STATE).split(":")[4]
        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        ussd_number = request.data.get("Mobile")
        request_payment(mobile_number, 3, ussd_number, get_network(payment_option), id_type, user_id, "Registration")

        return {
            "Message": "Thank you for applying for party updates. Please kindly confirm payment of mobile money phone "
                       "to complete process. "
                       " Charge is GHS 3.00",
            "Type": RELEASE_USSD
        }


def handle_payment(request, level):
    # method info #
    state_branch = 0
    next_level = int(level) + 1

    if level == 1:
        return {
            "Message": "Please select your ID type.\n\n1. Voter's ID\n2. Membership ID",
            "ClientState": "%d:%d" % (state_branch, next_level),
            "Type": RESPONSE_USSD
        }

    if level == 2:
        id_type = request.data.get(MESSAGE)
        actual_id = ["Voters", "Membership"][int(id_type) - 1]
        return {
            "Message": "Please enter you %s ID number" % actual_id,
            "ClientState": "%d:%d:%s" % (state_branch, next_level, id_type),
            "Type": RESPONSE_USSD
        }

    if level == 3:
        user_id = request.data.get(MESSAGE)
        id_type = request.data.get(CLIENT_STATE).split(":")[2]
        return {
            "Message": "Please select a payment method.\n\n1. MTN Mobile Money\n2. Airtel Money\n",
            "ClientState": "%d:%d:%s:%s" % (state_branch, next_level, id_type, user_id),
            "Type": RESPONSE_USSD
        }

    if level == 4:
        payment_option = request.data.get(MESSAGE)
        if not (payment_option in [str(a) for a in range(1, 3)]):
            return invalid_option_data

        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        return {
            "Message": "Please enter your mobile money phone number",
            "ClientState": "%d:%d:%s:%s:%s" % (state_branch, next_level, id_type, user_id, payment_option),
            "Type": RESPONSE_USSD
        }

    if level == 5:
        mobile_number = request.data.get(MESSAGE)

        payment_option = request.data.get(CLIENT_STATE).split(":")[4]
        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        if len(mobile_number) != 10:
            return {
                "Message": "The mobile number you provided is incorrect. Please try again.",
                "Type": RELEASE_USSD
            }

        payment_option_value = get_network(payment_option)

        ussd_number = request.data.get("Mobile")
        request_payment(mobile_number, 1, ussd_number, payment_option_value, id_type, user_id, "Dues - Ordinary")

        return {
            "Message": "Thank you for initiating dues payment (GHS 1.00). Kindly confirm payment on mobile money "
                       "phone to complete process.",
            "Type": RELEASE_USSD
        }


def handle_payment_executive(request, level):
    # method info #
    state_branch = 1
    next_level = int(level) + 1

    if level == 1:
        return {
            "Message": "Please select your ID type.\n\n1. Voter's ID\n2. Membership ID",
            "ClientState": "%d:%d" % (state_branch, next_level),
            "Type": RESPONSE_USSD
        }

    if level == 2:
        id_type = request.data.get(MESSAGE)
        actual_id = ["Voters", "Membership"][int(id_type) - 1]
        return {
            "Message": "Please enter you %s ID number" % actual_id,
            "ClientState": "%d:%d:%s" % (state_branch, next_level, id_type),
            "Type": RESPONSE_USSD
        }

    if level == 3:
        user_id = request.data.get(MESSAGE)
        id_type = request.data.get(CLIENT_STATE).split(":")[2]
        return {
            "Message": "Please select a payment method.\n\n1. MTN Mobile Money\n2. Airtel Money",
            "ClientState": "%d:%d:%s:%s" % (state_branch, next_level, id_type, user_id),
            "Type": RESPONSE_USSD
        }

    if level == 4:
        payment_option = request.data.get(MESSAGE)
        if not (payment_option in [str(a) for a in range(1, 3)]):
            return invalid_option_data

        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        return {
            "Message": "Please enter your mobile money phone number",
            "ClientState": "%d:%d:%s:%s:%s" % (state_branch, next_level, id_type, user_id, payment_option),
            "Type": RESPONSE_USSD
        }

    if level == 5:
        mobile_number = request.data.get(MESSAGE)

        payment_option = request.data.get(CLIENT_STATE).split(":")[4]
        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        payment_option_value = get_network(payment_option)

        if len(mobile_number) != 10:
            return {
                "Message": "The mobile number you provided is incorrect. Please try again.",
                "Type": RELEASE_USSD
            }

        ussd_number = request.data.get("Mobile")
        request_payment(mobile_number, 10, ussd_number, payment_option_value, id_type, user_id, "Dues - Executive")

        return {
            "Message": "Thank you for initiating dues payment (GHS 10.00). Kindly confirm payment on mobile money "
                       "phone to complete process.",
            "Type": RELEASE_USSD
        }


def payment_intermediary(request, level):
    return {
        "Message": "Please select one of the following.\n1. Ordinary Member (GHS 1.00)\n2. Executive Member (GHS 10.00)",
        "Type": RESPONSE_USSD,
        "ClientState": INITIAL_CLIENT_STATE
    }


@api_view(['POST'])
def index(request):
    branching_methods = [handle_payment, handle_payment_executive, handle_registration]

    sequence = request.data.get('Sequence', 0)

    # user has dialed code
    if sequence == 1:
        data = {
            "Type": RESPONSE_USSD,
            "Message": "Please select an option.\n\n1. Pay Dues"
                       "\n2. Register to receive party messages ("
                       "GHS 3.00)",
            "ClientState": INITIAL_CLIENT_STATE
        }

        return Response(data)

    # user has made selection
    if sequence == 2:
        client_state = request.data.get(CLIENT_STATE)

        # the person just began from the first
        # screen
        if client_state == INITIAL_CLIENT_STATE:
            user_response = request.data.get(MESSAGE)
            if not (user_response in [OPTION_PAY_DUES_ORDINARY, OPTION_REGISTER_MEMBER, ]):
                # the user did not select any of the valid options
                return Response(invalid_option_data)

            # now branch to actual method
            if user_response == OPTION_PAY_DUES_ORDINARY:
                return Response(payment_intermediary(request, 1))

            if user_response == OPTION_REGISTER_MEMBER:
                return Response(handle_registration(request, 1))

    if sequence == 3:
        user_choice = request.data.get("Message", "0")
        if not (user_choice in [str(a) for a in range(1, 3)]):
            return Response(invalid_option_data)

        if user_choice == "1":
            return Response(handle_payment(request, 1))

        elif user_choice == "2":
            return Response(handle_payment_executive(request, 1))

    if sequence > 3:
        client_state = request.data.get(CLIENT_STATE)
        branching_level_data = client_state.split(":")[:2]

        # now branch to method to handle handle request
        # notes on this is found at the top of this file
        branching_method_position = int(branching_level_data[0])
        branching_level = int(branching_level_data[1])
        return Response(branching_methods[branching_method_position](request, branching_level))
