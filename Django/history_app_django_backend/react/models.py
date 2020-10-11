from django.db import models


class Items(models.Model):
    item_number = models.CharField(max_length=4, blank=False, null=False, primary_key=True)
    title = models.CharField(max_length=40)
    image = models.ImageField(upload_to="item_images")
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Items"

    def __str__(self):
        return f'{self.item_number} : {self.title}'


class Filters(models.Model):
    item_number = models.OneToOneField(
        Items, on_delete=models.CASCADE, primary_key=True)
    query_language_filter = models.TextField()

    class Meta:
        verbose_name_plural = "Filters"

    def __str__(self):
        return self.item_number


class FAQ(models.Model):
    item_number = models.ForeignKey(Items, on_delete=models.CASCADE)
    question = models.CharField(max_length=300)
    answer = models.TextField()

    class Meta:
        verbose_name_plural = "FAQs"

    def __str__(self):
        return f'{self.item_number}, {self.question}'
