from django import forms


class RequestForm(forms.Form):
    """UC-06 · ไม่มีช่องเหตุผล · กรณีพิเศษบังคับวันที่คืน"""

    is_special = forms.BooleanField(label="⚡ ขอยืมระยะยาวเป็นกรณีพิเศษ", required=False)
    custom_due_date = forms.DateField(label="วันที่ต้องการคืน", required=False,
                                      widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        data = super().clean()
        if data.get("is_special") and not data.get("custom_due_date"):
            self.add_error("custom_due_date", "กรุณาระบุวันที่ต้องการคืนสำหรับการขอยืมกรณีพิเศษ")
        return data
