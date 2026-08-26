
from rest_framework import serializers

from education.models import Term


class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = ['id', 'start_date', 'end_date', 'type', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if start_date and start_date.day != 1:
            raise serializers.ValidationError({"start_date": "تاریخ شروع ترم باید اول ماه باشد."})

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({"end_date": "تاریخ پایان ترم باید بعد از تاریخ شروع باشد."})

            overlapping_terms = Term.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            )

            if self.instance:
                overlapping_terms = overlapping_terms.exclude(pk=self.instance.pk)

            if overlapping_terms.exists():
                raise serializers.ValidationError({"start_date": "بازه زمانی این ترم با یک ترم دیگر همپوشانی دارد."})

        return attrs