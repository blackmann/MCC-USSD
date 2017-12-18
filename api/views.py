from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.payment_executive import handle_payment_executive
from api.payment_ordinary import handle_payment_ordinary
from api.registration import handle_registration
from api.payment_sympathizer import handle_payment_sympathizer
from api.util import *


def payment_intermediary(request, level):
    return {
        "Message": "Please select one of the following.\n"
                   "1. General Member (GHS 1.00)\n"
                   "2. Executive Member (GHS 5.00)\n"
                   "3. Sympathizer",
        "Type": RESPONSE_USSD,
        "ClientState": BRANCH_B
    }


@api_view(['POST'])
def index(request):
    branching_methods = [handle_payment_ordinary,
                         handle_payment_executive,
                         handle_payment_sympathizer,
                         handle_registration]

    sequence = request.data.get('Sequence', 0)

    if sequence == 1:
        data = {
            "Type": RESPONSE_USSD,
            "Message": "NDC Payment Platform\n\n"
                       "Please select an option.\n\n"
                       "1. Pay Dues"
                       "\n2. Party Agents",
        }

        return Response(data)

    if sequence == 2:
        user_choice = request.data.get(MESSAGE)

        if not (user_choice in (str(a) for a in range(1, 3))):
            return Response(invalid_option_data)

        if user_choice == "2":
            pass

        else:
            data = {
                "Type": RESPONSE_USSD,
                "Message": "Please select an option.\n\n"
                           "1. Pay Dues"
                           "\n2. Register to receive party messages ("
                           "GHS 1.00)",
                "ClientState": BRANCH_B
            }

            return Response(data)

    # user has made selection
    if sequence == 3:
        client_state = request.data.get(CLIENT_STATE)

        # the person just began from the first
        # screen
        if client_state == BRANCH_B:
            user_response = request.data.get(MESSAGE)
            if not (user_response in [OPTION_PAY_DUES_ORDINARY, OPTION_REGISTER_MEMBER, ]):
                # the user did not select any of the valid options
                return Response(invalid_option_data)

            # now branch to actual method
            if user_response == OPTION_PAY_DUES_ORDINARY:
                return Response(payment_intermediary(request, 1))

            if user_response == OPTION_REGISTER_MEMBER:
                return Response(handle_registration(request, 1))

        else:
            pass

    if sequence == 4:
        head_branch = request.data.get(CLIENT_STATE).split(":")[0]
        if head_branch == BRANCH_B:
            state_branch = request.data.get(CLIENT_STATE).split(":")[1]
            if state_branch == "3":
                # increase the sequence to continue process
                sequence = sequence + 1
            else:
                user_choice = request.data.get("Message", "0")
                if not (user_choice in [str(a) for a in range(1, 4)]):
                    return Response(invalid_option_data)

                if user_choice == "1":
                    return Response(handle_payment_ordinary(request, 1))

                elif user_choice == "2":
                    return Response(handle_payment_executive(request, 1))

                elif user_choice == "3":
                    return Response(handle_payment_sympathizer(request, 1))

        else:
            pass

    if sequence > 4:
        head_branch = request.data.get(CLIENT_STATE).split(":")[0]
        if head_branch == BRANCH_B:
            client_state = request.data.get(CLIENT_STATE)
            branching_level_data = client_state.split(":")[1:3]

            # now branch to method to handle handle request
            # notes on this is found at the top of this file
            branching_method_position = int(branching_level_data[0])
            branching_level = int(branching_level_data[1])
            return Response(branching_methods[branching_method_position](request, branching_level))

        else:
            pass
