from rest_framework import serializers
from .models import SystemSettings

class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ["min_rate","max_rate","min_asset_value","max_asset_value","company_capital","min_threshold","report_email","updated_at"]
        read_only_fields = ["updated_at"]
