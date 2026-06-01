from .models import DentalChart, Tooth
from .fdi import teeth_for


def get_or_create_chart(patient, dentition="ADULT"):
    """Return the patient's chart, creating it (and its teeth) if needed."""
    chart, created = DentalChart.objects.get_or_create(
        patient=patient, defaults={"dentition": dentition}
    )
    if created or not chart.teeth.exists():
        Tooth.objects.bulk_create(
            [
                Tooth(chart=chart, fdi_number=num, name=name)
                for num, name in teeth_for(chart.dentition)
            ],
            ignore_conflicts=True,
        )
    return chart
