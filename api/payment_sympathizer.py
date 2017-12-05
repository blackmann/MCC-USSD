from api.util import *


def handle_payment_sympathizer(request, level):
    # method info #
    state_branch = 2
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
            "Message": "Please specify amount you want to pay.",
            "ClientState": "%d:%d:%s:%s" % (state_branch, next_level, id_type, user_id),
            "Type": RESPONSE_USSD
        }

    if level == 4:
        amount = request.data.get(MESSAGE)
        id_type = request.data.get(CLIENT_STATE).split(":")[2]
        user_id = request.data.get(CLIENT_STATE).split(":")[3]

        try:
            parsed_amount = float(amount)

            return {
                "Message": "Please select a payment method.\n\n"
                           "1. MTN Mobile Money\n"
                           "2. Airtel Money",
                "ClientState": "%d:%d:%s:%s:%.2f" % (state_branch, next_level, id_type, user_id, parsed_amount),
                "Type": RESPONSE_USSD
            }
        except ValueError:
            return {
                "Message": "The amount you specified is invalid. Should be in the form 8.50 or 5",
                "Type": RELEASE_USSD
            }

    if level == 5:
        payment_option = request.data.get(MESSAGE)
        if not (payment_option in [str(a) for a in range(1, 3)]):
            return invalid_option_data

        amount = request.data.get(CLIENT_STATE).split(":")[4]
        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        return {
            "Message": "Please enter your mobile money phone number",
            "ClientState": "%d:%d:%s:%s:%.2f:%s" % (state_branch, next_level, id_type, user_id, amount, payment_option),
            "Type": RESPONSE_USSD
        }

    if level == 6:
        mobile_number = request.data.get(MESSAGE)

        payment_option = request.data.get(CLIENT_STATE).split(":")[5]
        amount = request.data.get(CLIENT_STATE).split(":")[4]
        user_id = request.data.get(CLIENT_STATE).split(":")[3]
        id_type = request.data.get(CLIENT_STATE).split(":")[2]

        payment_option_value = get_network(payment_option)

        if len(mobile_number) != 10:
            return {
                "Message": "The mobile number you provided is incorrect. Please try again.",
                "Type": RELEASE_USSD
            }

        ussd_number = request.data.get("Mobile")
        request_payment(mobile_number,
                        float(amount),
                        ussd_number,
                        payment_option_value,
                        id_type,
                        user_id, "Dues - Sympathizer")

        return {
            "Message": "Thank you for initiating dues payment GHS %.2f. Kindly confirm payment on mobile money "
                       "phone to complete process." % amount,
            "Type": RELEASE_USSD
        }
