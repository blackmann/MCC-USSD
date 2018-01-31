from api.util import *


def handle_payment_ordinary(request, level):
    # method info #
    state_branch = 0
    next_level = int(level) + 1

    if level == 1:
        return {
            "Message": "Please select your ID type.\n\n"
                       "1. Voter's ID\n"
                       "2. Membership ID",
            "ClientState": "%s:%d:%d" % (BRANCH_A, state_branch, next_level),
            "Type": RESPONSE_USSD
        }

    if level == 2:
        id_type = request.data.get(MESSAGE)
        actual_id = ["Voters", "Membership"][int(id_type) - 1]
        return {
            "Message": "Please enter you %s ID number" % actual_id,
            "ClientState": "%s:%d:%d:%s" % (BRANCH_A, state_branch, next_level, id_type),
            "Type": RESPONSE_USSD
        }

    if level == 3:
        user_id = request.data.get(MESSAGE)
        id_type = request.data.get(CLIENT_STATE).split(":")[3]
        return {
            "Message": "Please select a payment method.\n\n1. MTN Mobile Money\n2. Airtel Money\n",
            "ClientState": "%s:%d:%d:%s:%s" % (BRANCH_A, state_branch, next_level, id_type, user_id),
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
            "ClientState": "%s:%d:%d:%s:%s:%s" % (BRANCH_A, state_branch, next_level, id_type, user_id, payment_option),
            "Type": RESPONSE_USSD
        }

    if level == 5:
        mobile_number = request.data.get(MESSAGE)

        payment_option = request.data.get(CLIENT_STATE).split(":")[5]
        user_id = request.data.get(CLIENT_STATE).split(":")[4]
        id_type = request.data.get(CLIENT_STATE).split(":")[3]

        if len(mobile_number) != 10:
            return {
                "Message": "The mobile number you provided is incorrect. Please try again.",
                "Type": RELEASE_USSD
            }

        payment_option_value = get_network(payment_option)

        ussd_number = request.data.get("Mobile")
        request_payment(mobile_number, 1, ussd_number, payment_option_value, id_type, user_id, "Dues - General")

        return {
            "Message": "Thank you for initiating dues payment (GHS 1.00). Kindly confirm payment on mobile money "
                       "phone to complete process.",
            "Type": RELEASE_USSD
        }
