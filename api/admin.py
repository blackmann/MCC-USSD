from django.contrib import admin

from api.models import Member, Payment

admin.site.register((Member, Payment, ))
