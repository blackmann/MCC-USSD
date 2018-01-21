from api.models import Registration
from api.pins import pins
from api.util import *
from api.send_registrations import send_registration


def party_agent(request, level):
    if level == 1:
        return {
            "Type": RESPONSE_USSD,
            "Message": "Please enter your password",
            "ClientState": "%s" % BRANCH_C
        }

    if level == 2:
        password = request.data.get(MESSAGE)

        if not (password in pins):
            return {
                "Type": RELEASE_USSD,
                "Message": "Sorry the pin you entered is incorrect. Please try again!",
            }

        return {
            "Type": RESPONSE_USSD,
            "Message": "Enter name of Member",
            "ClientState": "%s:%s" % (BRANCH_C, password),
        }

    if level == 3:
        member_name = request.data.get(MESSAGE)
        password = request.data.get(CLIENT_STATE).split(':')[1]

        return {
            "Type": RESPONSE_USSD,
            "Message": "Enter the ID of the member",
            "ClientState": "%s:%s:%s" % (BRANCH_C, password, member_name)
        }

    if level == 4:
        member_id = request.data.get(MESSAGE)
        member_name = request.data.get(CLIENT_STATE).split(":")[2]
        password = request.data.get(CLIENT_STATE).split(":")[1]

        reg = Registration(agent_pin=password,
                           member_name=member_name,
                           member_id=member_id)

        import threading

        thread = threading.Thread(target=send_registration,
                                  args=(reg, ))
        thread.daemon = True
        thread.start()

        return {
            "Type": RELEASE_USSD,
            "Message": "Input successful. Thank you."
        }
