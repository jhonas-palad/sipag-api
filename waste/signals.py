from django.db.models.signals import ModelSignal

waste_report_action = ModelSignal(use_caching=True)
