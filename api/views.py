import json

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

OPTION_PAY_DUES = "1"
OPTION_REGISTER_MEMBER = "2"

invalid_option_data = {
    "Type": RELEASE_USSD,
    "Message": "The option you selected is not valid. Please try again!"
}


def check_validity(mobile_number):
    return False


def request_payment(mobile_number, amount, constituency, network):
    response = requests.post("https://payment.mypayutil.com/api/users/authenticate",
                             data={"mobileNumber": "0000000006",
                                   "password": "memberReg#Newdeveloper5"})

    if str(response.status_code).startswith("20"):
        json_response = response.json()
        access_token = json_response['access_token']

        request_body = {
            "mobileNumber": mobile_number,
            "source": "USSD",
            "thirdPartyRef": "N/A",
            "amount": amount,
            "parameters": {
                "Member Constituency": constituency
            }
        }

        headers = {
            "Authorization": "Bearer %s" % access_token
        }

        requests.post("https://payment.mypayutil.com/api/merchants/payments/%s" % network,
                      data=request_body,
                      headers=headers)


def handle_registration(request, level):
    state_branch = 1
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
                           "Money\n2. Aitel/Tigo Money",
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
            "Message": "Please select a payment method.\n\n1. MTN Mobile Money\n2. Airtel/Tigo Cash",
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

        payment_option_value = ["mtn", "airtel"][int(payment_option) - 1]

        if len(mobile_number) != 10:
            return {
                "Message": "The mobile number you provided is incorrect. Please try again.",
                "Type": RELEASE_USSD
            }

        request_payment(request.data.get("Mobile"), 1, "N/A", payment_option_value)

        return {
            "Message": "Thank you for initiating dues payment (GHS 1.00). Kindly confirm payment on mobile money "
                       "phone to complete process.",
            "Type": RELEASE_USSD
        }


@api_view(['POST'])
def index(request):
    branching_methods = [handle_payment, handle_registration]

    sequence = request.data.get('Sequence', 0)

    # user has dialed code
    if sequence == 1:
        data = {
            "Type": RESPONSE_USSD,
            "Message": "Please select an option.\n\n1. Pay Dues (GHS 1.00)\n2. Register to receive party messages ("
                       "GHS 3.00)",
            "ClientState": INITIAL_CLIENT_STATE
        }

        return Response(data)

    # user has made selection
    if sequence == 2:
        client_state = request.data.get(CLIENT_STATE)

        # when client state is 1, the person just began from the first
        # screen
        if client_state == INITIAL_CLIENT_STATE:
            user_response = request.data.get(MESSAGE)
            if not (user_response in [OPTION_PAY_DUES, OPTION_REGISTER_MEMBER, ]):
                # the user did not select any of the valid options
                return Response(invalid_option_data)

            # now branch to actual method
            if user_response == OPTION_PAY_DUES:
                return Response(handle_payment(request, 1))

            if user_response == OPTION_REGISTER_MEMBER:
                return Response(handle_registration(request, 1))

    if sequence > 2:
        client_state = request.data.get(CLIENT_STATE)
        branching_level_data = client_state.split(":")[:2]

        # now branch to method to handle handle request
        # notes on this is found at the top of this file
        branching_method_position = int(branching_level_data[0])
        branching_level = int(branching_level_data[1])
        return Response(branching_methods[branching_method_position](request, branching_level))
