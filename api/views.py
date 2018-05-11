import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from api.models import Registration
from api.option_1 import option_1
from api.party_agent import party_agent
from api.util import BRANCH_A, BRANCH_B, CLIENT_STATE, MESSAGE, RESPONSE_USSD, \
    invalid_option_data, send_payment_data


@api_view(['POST'])
def index(request):
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

        if user_choice == "2":
            # Party agent branch
            return Response(party_agent(request, 1) or invalid_option_data)

        if user_choice == "1":
            # Dues payment branch
            return Response(option_1(request, 1) or invalid_option_data)

    if sequence > 2:
        level = sequence - 1
        branch = request.data.get(CLIENT_STATE).split(":")[0]

        # adding `or invalid_option_data` to all responses
        # to handle all cases of incorrect input from the
        # branching methods. This way we wont be returning
        # invalid... for every level in the branches

        if branch == BRANCH_B:
            # Party agent branch
            return Response(party_agent(request, level) or invalid_option_data)

        if branch == BRANCH_A:
            # Dues payment branch
            return Response(option_1(request, level) or invalid_option_data)

    return Response(invalid_option_data)


class RegistrationSerializer(ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'


@api_view(['GET'])
def get_registrations(request):
    registrations = Registration.objects.all()
    data = RegistrationSerializer(registrations, many=True).data

    return Response(data)


@api_view(['POST'])
def forward_data(request, momo_n, mob, intent, id_type, mem_id, pay_ch):
    success = request.data['Data']['AmountAfterCharges'] > 0.0
    s = "false"
    if success:
        s = "true"

    amount = request.data['Data']['Amount']

    data = {
        "when": str(datetime.datetime.now()),
        "success": s,
        "mobile_money_number": momo_n,
        "mobile_number": mob,
        "intent": intent,
        "id_type": id_type,
        "member_id": mem_id,
        "mobile_money_network": pay_ch,
        "amount_paid": str(amount),
        "auth": "~ragnal~&*$^#",
        "status": "COMPLETE"
    }

    send_payment_data(data)

    return Response()

    
