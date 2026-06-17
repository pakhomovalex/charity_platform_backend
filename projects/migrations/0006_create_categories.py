from django.db import migrations

def add_categories(apps, schema_editor):
    Category = apps.get_model('projects', 'Category')
    categories = [
        {'name': 'Діджитал арт', 'slug': 'didzhital-art'},
        {'name': 'Дім та декор', 'slug': 'dim-ta-dekor'},
        {'name': 'Мистецтво', 'slug': 'mistectvo'},
        {'name': 'Настільні ігри та іграшки', 'slug': 'nastilni-igri-ta-igrashki'},
        {'name': 'Одяг', 'slug': 'odyag'},
        {'name': 'Прикраси та аксесуари', 'slug': 'prikrasi-ta-aksesuary'},
    ]
    for cat in categories:
        Category.objects.get_or_create(slug=cat['slug'], defaults=cat)

class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0005_remove_projectimage_image_original_and_more'),  # или твоя последняя миграция
    ]
    operations = [
        migrations.RunPython(add_categories),
    ]