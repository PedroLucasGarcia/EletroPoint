from django.db import migrations

def remove_images(apps, schema_editor):
    Product = apps.get_model('store', 'Product')

    for product in Product.objects.all():
        product.image = None
        product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_orderitem_color_image'),
    ]

    operations = [
        migrations.RunPython(remove_images),
    ]