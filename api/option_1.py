from api.util import RESPONSE_USSD, BRANCH_A, MESSAGE, CLIENT_STATE, RELEASE_USSD, request_payment, get_network

SPAN_MENU = "Please select the span of your payment:\n\n" \
            "1. 1 month\n" \
            "2. 6 months\n" \
            "3. 12 months\n" \
            "4. 2 years"

ID_TYPE_MENU = "Please select your ID type:\n\n" \
               "1. Voters ID\n" \
               "2. Membership ID"

ID_NUMBER_SCREEN = "Please enter your %s ID number:\n"

PAYMENT_METHOD_MENU = "Please select payment method type:\n\n" \
                      "1. MTN Mobile Money\n" \
                      "2. Airtel Money"

PAYMENT_NUMBER_SCREEN = "Please enter your %s number"

PERIODS = [
    ("1 month", 1),
    ("6 months", 6),
    ("12 months", 12),
    ("2 years", 24)
]

EXECUTIVES_AMOUNTS = [2, 5, 20, 50, ]

ID_TYPES = ["Voters", "Membership", ]


def option_1(request, level):
    if level == 1:
        return {
            "Type": RESPONSE_USSD,
            "Message": "Please select an option:\n\n"
                       "1. General Member (1.00/Month)\n"
                       "2. Party Official\n"
                       "3. Donor (Open)\n",
            "ClientState": BRANCH_A
        }

    if level == 2:
        user_input = request.data.get(MESSAGE)
        new_client_state = "%s:%s" % (BRANCH_A, user_input)

        if user_input == "1":
            # General Member
            return {
                "Type": RESPONSE_USSD,
                "Message": SPAN_MENU,
                "ClientState": new_client_state
            }

        if user_input == "2":
            # Executives menu (SELECTED OFFICIAL)
            return {
                "Type": RESPONSE_USSD,
                "Message": "Please your level:\n\n"
                           "1. Branch Execut. (2.0/Month)\n"
                           "2. Constituency Exec. (5.0/Month)\n"
                           "3. Regional Exec. (20.0/Month)\n"
                           "4. National Exec. (50.0/Month)\n",
                "ClientState": new_client_state
            }

        if user_input == "3":
            # Donor menu
            return {
                "Type": RESPONSE_USSD,
                "Message": "Please specify an amount you want to donate.",
                "ClientState": new_client_state
            }

    # these variables are common in the following scenarios
    user_input = request.data.get(MESSAGE)
    old_client_state = request.data.get(CLIENT_STATE)
    new_client_state = "%s:%s" % (old_client_state, user_input)

    top_choice = old_client_state.split(":")[1]
    ussd_number = request.data.get("Mobile")

    if level == 3:
        if top_choice == "1":
            if not (user_input in (str(i) for i in range(1, 5))):
                return None
            # General Member
            return {
                "Type": RESPONSE_USSD,
                "Message": ID_TYPE_MENU,
                "ClientState": new_client_state
            }

        if top_choice == "2":
            if not (user_input in (str(i) for i in range(1, 5))):
                return None
            # Executive Member (SELECTED LEVEL)
            return {
                "Type": RESPONSE_USSD,
                "Message": SPAN_MENU,
                "ClientState": new_client_state
            }

        if top_choice == "3":
            # Donor
            if not user_input.isdigit():
                return None

            return {
                "Type": RESPONSE_USSD,
                "Message": ID_TYPE_MENU,
                "ClientState": new_client_state
            }

    if level == 4:
        if top_choice in ("1", "3",):
            # General Member, Donor
            if not (user_input in (str(a) for a in range(1, 3))):
                return None

            id_type = ["Voters", "Membership"][int(user_input) - 1]

            return {
                "Type": RESPONSE_USSD,
                "Message": ID_NUMBER_SCREEN % id_type,
                "ClientState": new_client_state
            }

        if top_choice == "2":
            # Executive (SELECTED SPAN)
            if not (user_input in (str(i) for i in range(1, 5))):
                return None

            return {
                "Type": RESPONSE_USSD,
                "Message": ID_TYPE_MENU,
                "ClientState": new_client_state
            }

    if level == 5:
        if top_choice in ("1", "3",):
            # General Member, Donor

            return {
                "Type": RESPONSE_USSD,
                "Message": PAYMENT_METHOD_MENU,
                "ClientState": new_client_state
            }

        if top_choice == "2":
            # Executive (SELECTED SPAN)
            if not (user_input in (str(a) for a in range(1, 3))):
                return None

            id_type = ["Voters", "Membership"][int(user_input) - 1]

            return {
                "Type": RESPONSE_USSD,
                "Message": ID_NUMBER_SCREEN % id_type,
                "ClientState": new_client_state
            }

    if level == 6:
        if top_choice in ("1", "3",):
            # General Member, Donor
            if not (user_input in (str(a) for a in range(1, 3))):
                return None

            payment_type = ["MTN Mobile Money", "Airtel Money"][int(user_input) - 1]

            return {
                "Type": RESPONSE_USSD,
                "Message": PAYMENT_NUMBER_SCREEN % payment_type,
                "ClientState": new_client_state
            }

        if top_choice == "2":
            # Executive
            return {
                "Type": RESPONSE_USSD,
                "Message": PAYMENT_METHOD_MENU,
                "ClientState": new_client_state
            }

    if level == 7:
        if top_choice in ("1", "3",):
            if len(user_input) != 10:
                # General, Donors
                return {
                    "Type": RELEASE_USSD,
                    "Message": "The phone number you provided should be 10 digits. Please try again!",
                }

            # do calculations
            if top_choice == "1":
                period_choice = int(new_client_state.split(":")[2]) - 1
                period = PERIODS[period_choice]
                amount = 1 * period[1]
                intent = "Dues - General Member: %s" % period[0]

            elif top_choice == "3":
                amount = float(new_client_state.split(":")[2])
                intent = "Dues - Donor"

            # safe proof
            else:
                return None

            selected_id_type = ID_TYPES[int(new_client_state.split(":")[3])-1]
            id_number = new_client_state.split(":")[4]

            network = get_network(new_client_state.split(":")[5])
            payment_number = new_client_state.split(":")[6]

            request_payment(payment_number,
                            amount,
                            ussd_number,
                            network,
                            selected_id_type,
                            id_number,
                            intent)

            return {
                "Type": RELEASE_USSD,
                "Message": "Thank you for initiating dues payment of GHS %.2f."
                           " Please confirm the payment on your mobile money "
                           "phone shortly." % amount
            }

        if top_choice == "2":
            # Executive
            if not (user_input in (str(a) for a in range(1, 3))):
                return None

            payment_type = ["MTN Mobile Money", "Airtel Money"][int(user_input) - 1]

            return {
                "Type": RESPONSE_USSD,
                "Message": PAYMENT_NUMBER_SCREEN % payment_type,
                "ClientState": new_client_state
            }

    if level == 8:
        # Executive left
        if top_choice == "2":
            if len(user_input) != 10:
                return {
                    "Type": RELEASE_USSD,
                    "Message": "The phone number you provided should be 10 digits. Please try again!",
                }

            # do calculations
            period_choice = int(new_client_state.split(":")[3]) - 1
            period = PERIODS[period_choice]
            executive_level_amount = EXECUTIVES_AMOUNTS[int(new_client_state.split(":")[3]) - 1]
            amount = executive_level_amount * period[1]
            intent = "Dues - General Member: %s" % period[0]

            selected_id_type = ID_TYPES[int(new_client_state.split(":")[4])-1]
            id_number = new_client_state.split(":")[5]

            network = get_network(new_client_state.split(":")[6])
            payment_number = new_client_state.split(":")[7]

            request_payment(payment_number,
                            amount,
                            ussd_number,
                            network,
                            selected_id_type,
                            id_number,
                            intent)

            return {
                "Type": RELEASE_USSD,
                "Message": "Thank you for initiating dues payment of GHS %.2f."
                           " Please confirm the payment on your mobile money "
                           "phone shortly." % amount
            }
