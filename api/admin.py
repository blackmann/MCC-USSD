from django.contrib import admin

from api.models import Member, Payment, Registration

admin.site.register((Member, Payment, Registration, ))
