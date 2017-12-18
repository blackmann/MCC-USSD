from api.util import *


def handle_registration(request, level):
    state_branch = 3
    next_level = int(level) + 1

    # the person has provided constituency
    if level == 1:
        return {
            "Message": "Please select a ID type.\n\n"
                       "1. Voter's ID\n"
                       "2. Membership ID",
            "ClientState": "%s:%d:%d" % (BRANCH_B, state_branch, next_level,),
            "Type": RESPONSE_USSD
        }

    if level == 2:
        user_id_type = request.data.get(MESSAGE)

        return {
            "Message": "Please enter your ID Number",
            "ClientState": "%s:%d:%d:%s" % (BRANCH_B, state_branch, next_level, user_id_type),
            "Type": RESPONSE_USSD
        }

    if level == 3:
        user_id = request.data.get(MESSAGE)
        user_id_type = request.data.get(CLIENT_STATE).split(":")[3]

        return {
            "Message": "Please select a payment method to pay registration fee of GHS 1.00\n\n"
                       "1. MTN Mobile Money\n"
                       "2. Airtel Money",
            "ClientState": "%s:%d:%d:%s:%s" % (BRANCH_B, state_branch, next_level, user_id_type, user_id),
            "Type": RESPONSE_USSD
        }

    if level == 4:
        payment_option = request.data.get(MESSAGE)
        if not (payment_option in [str(a) for a in range(1, 3)]):
            return invalid_option_data

        user_id = request.data.get(CLIENT_STATE).split(":")[4]
        id_type = request.data.get(CLIENT_STATE).split(":")[3]

        return {
            "Message": "Please enter your mobile money phone number",
            "ClientState": "%s:%d:%d:%s:%s:%s" % (BRANCH_B, state_branch, next_level, id_type, user_id, payment_option),
            "Type": RESPONSE_USSD
        }

    if level == 5:
        mobile_number = request.data.get(MESSAGE)
        if len(mobile_number) != 10:
            return invalid_option_data

        payment_option = request.data.get(CLIENT_STATE).split(":")[5]
        user_id = request.data.get(CLIENT_STATE).split(":")[4]
        id_type = request.data.get(CLIENT_STATE).split(":")[3]

        ussd_number = request.data.get("Mobile")
        request_payment(mobile_number, 1, ussd_number, get_network(payment_option), id_type, user_id, "Registration")

        return {
            "Message": "Thank you for applying for party updates. Please kindly confirm payment on mobile money phone "
                       "to complete process. "
                       " Charge is GHS 1.00",
            "Type": RELEASE_USSD
        }

