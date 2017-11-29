from rest_framework.decorators import api_view
from rest_framework.response import Response

# Notes
# ClientState is structured in the form 'branching_method':'current_level' then other data
# follow -> 1:2:Degreat Yartey:Alogboshie:1:etc
# this is used to determine which level the user has gotten to and what to show
from api.models import Member

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


def create_member(user_name, constituency,
                  user_id_type, user_id):
    """

    :param user_name:
    :param constituency:
    :param user_id_type: is the position in the menu for id type
    :param user_id:
    :return:
    """
    actual_id_type = ["Voters", "Member ID"][int(user_id_type) - 1]
    member_exists = Member.objects.filter(id_type=actual_id_type,
                                          member_id=user_id).exists()

    if not member_exists:
        Member.objects.create(name=user_name,
                              id_type=actual_id_type,
                              member_id=user_id,
                              constituency=constituency)

    return not member_exists


def handle_registration(request, level):
    state_branch = 1
    next_level = int(level) + 1

    if level == 1:
        return {
            "Message": "Please enter your name (First and last name)",
            "ClientState": "%d:%d" % (state_branch, next_level),
            "Type": RESPONSE_USSD
        }

    # the person has provided name
    if level == 2:
        user_name = request.data.get(MESSAGE)
        return {
            "Message": "Please enter you constituency",
            "ClientState": "%d:%d:%s" % (state_branch, next_level, user_name),
            "Type": RESPONSE_USSD
        }

    # the person has provided constituency
    if level == 3:
        constituency = request.data.get(MESSAGE)
        user_name = request.data.get(CLIENT_STATE).split(":")[2]
        return {
            "Message": "Please select a ID type.\n\n1. Voter's ID\n2. Membership ID",
            "ClientState": "%d:%d:%s:%s" % (state_branch, next_level, user_name, constituency),
            "Type": RESPONSE_USSD
        }

    if level == 4:
        user_id_type = request.data.get(MESSAGE)
        constituency = request.data.get(CLIENT_STATE).split(":")[3]
        user_name = request.data.get(CLIENT_STATE).split(":")[2]

        return {
            "Message": "Please enter your ID Number",
            "ClientState": "%d:%d:%s:%s:%s" % (state_branch, next_level, user_name, constituency, user_id_type),
            "Type": RESPONSE_USSD
        }

    if level == 5:
        user_id = request.data.get(MESSAGE)
        user_id_type = request.data.get(CLIENT_STATE).split(":")[4]
        constituency = request.data.get(CLIENT_STATE).split(":")[3]
        user_name = request.data.get(CLIENT_STATE).split(":")[2]

        if create_member(user_name, constituency, user_id_type, user_id):
            return {
                "Message": "Dear %s, you have been registered as a member successfully. " % user_name,
                "Type": RELEASE_USSD
            }

        else:
            return {
                "Message": "A member has already been registered with the ID you provided.",
                "Type": RELEASE_USSD
            }


def handle_payment(request, level):
    # method info #
    state_branch = 0
    next_level = int(level) + 1

    if level == 1:
        return {
            "Message": "Please enter your name (First and last name)",
            "ClientState": "%d:%d" % (state_branch, next_level),
            "Type": RESPONSE_USSD
        }

    # the person provides her name here
    if level == 2:
        user_name = request.data.get(MESSAGE)
        return {
            "Message": "Please enter you constituency",
            "ClientState": "%d:%d:%s" % (state_branch, next_level, user_name),
            "Type": RESPONSE_USSD
        }

    # the person provides her constituency
    if level == 3:
        constituency = request.data.get(MESSAGE)
        user_name = request.data.get(CLIENT_STATE).split(":")[2]
        return {
            "Message": "Please select a payment method.\n\n1. MTN Mobile Money\n2. Airtel Money\n3. Tigo Cash",
            "ClientState": "%d:%d:%s:%s" % (state_branch, next_level, user_name, constituency),
            "Type": RESPONSE_USSD
        }

    if level == 4:
        payment_option = request.data.get(MESSAGE)
        if not (payment_option in [str(a) for a in range(1, 4)]):
            return invalid_option_data

        constituency = request.data.get(CLIENT_STATE).split(":")[3]
        user_name = request.data.get(CLIENT_STATE).split(":")[2]

        return {
            "Message": "Thank you %s for initiating dues payment (GHS 1.00). Kindly confirm payment on mobile money "
                       "phone to complete process. " % user_name,
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
            "Message": "Please select an option.\n\n1. Pay Dues\n2. Register as member",
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
