"""One-off sample-data seeder. Run: python manage.py shell < seed_data.py
Bilingual (English/Arabic) demo content. Safe to re-run: uses get_or_create."""
from farm.models import Farm
from crops.models import Crop, CropBasemap, Plant, PlantAttribute, PlantAttributeValue

# --- Farm ---
farm, _ = Farm.objects.get_or_create(
    name="مزرعة النخيل / Palm Farm",
    defaults=dict(location="القصيم / Al-Qassim", lat=26.33, lng=43.97),
)

# --- Crops ---
dates, _ = Crop.objects.get_or_create(farm=farm, name="تمر / Dates", defaults=dict(type="fruit"))
wheat, _ = Crop.objects.get_or_create(farm=farm, name="قمح / Wheat", defaults=dict(type="grain"))

# --- Basemap for the dates crop ---
CropBasemap.objects.get_or_create(
    crop=dates,
    image_uri="https://example.com/basemaps/dates.jpg",
    defaults=dict(source="user_upload", width_px=2000, height_px=1500, is_active=True),
)

# --- Plants on the dates crop (img_x/img_y normalized 0..1) ---
plants_spec = [
    ("نخلة 1 / Palm 1", 0.20, 0.30, "#4F8F2C", False, False),
    ("نخلة 2 / Palm 2", 0.55, 0.40, "#4F8F2C", True,  True),
    ("نخلة 3 / Palm 3", 0.80, 0.65, "#8B5A2B", False, True),
]
created_plants = []
for label, x, y, color, special, care in plants_spec:
    p, _ = Plant.objects.get_or_create(
        crop=dates, label=label,
        defaults=dict(img_x=x, img_y=y, color=color, type="palm",
                      is_special=special, needs_care=care, age_months=36),
    )
    created_plants.append(p)

# --- Plant attributes (user-defined fields) + example values ---
attr_water, _ = PlantAttribute.objects.get_or_create(
    crop=dates, name="يحتاج ري / Needs water", defaults=dict(value_type=PlantAttribute.BOOL))
attr_bunches, _ = PlantAttribute.objects.get_or_create(
    crop=dates, name="عدد العذوق / Bunches", defaults=dict(value_type=PlantAttribute.INT))
PlantAttributeValue.objects.get_or_create(attribute=attr_water, plant=created_plants[2], defaults=dict(value=True))
PlantAttributeValue.objects.get_or_create(attribute=attr_bunches, plant=created_plants[1], defaults=dict(value=8))

print("Farms:", Farm.objects.count())
print("Crops:", Crop.objects.count())
print("Basemaps:", CropBasemap.objects.count())
print("Plants:", Plant.objects.count())
print("PlantAttributes:", PlantAttribute.objects.count())
print("PlantAttributeValues:", PlantAttributeValue.objects.count())
