from django.contrib import admin
from .models import *
from solo.admin import SingletonModelAdmin

admin.site.register(LoadData)
admin.site.register(ConfigurationSetting, SingletonModelAdmin)
config = ConfigurationSetting.objects.get()
config = ConfigurationSetting.get_solo()
