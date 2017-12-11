from api.util import *


def handle_payment_sympathizer(request, level):
    # method info #
    state_branch = 2
    next_level = int(level) + 1

    if level == 1:
        return {
            "Message": "Please specify amount you want to pay.",
            "ClientState": "%d:%d" % (state_branch, next_level),
            "Type": RESPONSE_USSD
        }

    if level == 2:
        amount = request.data.get(MESSAGE)

        try:
            parsed_amount = float(amount)

            return {
                "Message": "Please select a payment method.\n\n"
                           "1. MTN Mobile Money\n"
                           "2. Airtel Money",
                "ClientState": "%d:%d:%.2f" % (state_branch, next_level, parsed_amount),
                "Type": RESPONSE_USSD
            }
        except ValueError:
            return {
                "Message": "The amount you specified is invalid. Should be in the form 8.50 or 5",
                "Type": RELEASE_USSD
            }

    if level == 3:
        payment_option = request.data.get(MESSAGE)
        if not (payment_option in [str(a) for a in range(1, 3)]):
            return invalid_option_data

        amount = request.data.get(CLIENT_STATE).split(":")[2]

        return {
            "Message": "Please enter your mobile money phone number",
            "ClientState": "%d:%d:%.2f:%s" % (state_branch,
                                              next_level,
                                              float(amount),
                                              payment_option),
            "Type": RESPONSE_USSD
        }

    if level == 4:
        mobile_number = request.data.get(MESSAGE)

        payment_option = request.data.get(CLIENT_STATE).split(":")[3]
        amount = request.data.get(CLIENT_STATE).split(":")[2]

        payment_option_value = get_network(payment_option)

        if len(mobile_number) != 10:
            return {
                "Message": "The mobile number you provided is incorrect. Please try again.",
                "Type": RELEASE_USSD
            }

        ussd_number = request.data.get("Mobile")

        import threading
        thread = threading.Thread(target=request_payment,
                                  args=(mobile_number,
                                        float(amount),
                                        ussd_number,
                                        payment_option_value,
                                        2,
                                        "N/A", "Dues - Sympathizer"))
        thread.daemon = True
        thread.start()

        return {
            "Message": "Thank you for initiating dues payment GHS %.2f. Kindly confirm payment on mobile money "
                       "phone to complete process." % float(amount),
            "Type": RELEASE_USSD
        }
