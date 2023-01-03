from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import pytz
from tinymce.models import HTMLField
from PIL import Image
from django.utils.translation import gettext_lazy as _


utc=pytz.UTC

# Create your models here.
class AutomobilioModelis(models.Model):
    gamintojas = models.CharField("Gamintojas", max_length=100)
    modelis = models.CharField("Modelis", max_length=100)

    def __str__(self):
        return f"{self.gamintojas} {self.modelis}"

    class Meta:
        verbose_name = "Automobilio modelis"
        verbose_name_plural = "Automobilio modeliai"

class Paslauga(models.Model):
    pavadinimas = models.CharField("Pavadinimas", max_length=200)
    kaina = models.FloatField("Kaina")

    def __str__(self):
        return f"{self.pavadinimas}"

    class Meta:
        verbose_name = "Paslauga"
        verbose_name_plural = "Paslaugos"

class Automobilis(models.Model):
    modelis = models.ForeignKey("AutomobilioModelis", on_delete=models.SET_NULL, null=True)
    valstybinis_nr = models.CharField("Valstybinis numeris", max_length=10)
    vin_kodas = models.CharField("VIN kodas", max_length=20)
    kliento_vardas = models.CharField("Kliento vardas", max_length=30)
    photo = models.ImageField('Nuotrauka', upload_to='automobiliai', null=True)
    aprasymas = HTMLField("Aprašymas", null=True, blank=True)

    def __str__(self):
        return f"{self.modelis} {self.valstybinis_nr} ({self.kliento_vardas})"

    class Meta:
        verbose_name = "Automobilis"
        verbose_name_plural = "Automobiliai"
        ordering = ['-id']

class Uzsakymas(models.Model):
    data = models.DateField(_("Date"), auto_now_add=True, blank=True)
    automobilis = models.ForeignKey("Automobilis", on_delete=models.SET_NULL, null=True, related_name="uzsakymai")
    vartotojas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    terminas = models.DateTimeField(_("Deadline"), null=True, blank=True)

    def praejes_terminas(self):
        if self.terminas and datetime.today().replace(tzinfo=utc) > self.terminas.replace(tzinfo=utc):
            return True
        return False

    praejes_terminas.short_description = _("Past deadline")

    def bendra(self):
        bendra = 0
        eilutes = self.eilutes.all()
        for eilute in eilutes:
            bendra += eilute.kiekis * eilute.paslauga.kaina
        return bendra

    bendra.short_description = _("Total")

    STATUS = (
        ("p", _("Confirmed")),
        ("v", _("In progress")),
        ("i", _("Completed")),
        ("a", _("Canceled")),
    )


    statusas = models.CharField(max_length=1, choices=STATUS, default="p", help_text="Statusas")

    def __str__(self):
        return f"{self.data} {self.automobilis}"

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-id']


class UzsakymoEilute(models.Model):
    uzsakymas = models.ForeignKey("Uzsakymas", on_delete=models.CASCADE, null=True, related_name="eilutes")
    paslauga = models.ForeignKey("Paslauga", on_delete=models.SET_NULL, null=True)
    kiekis = models.IntegerField("Kiekis")

    def suma(self):
        return self.kiekis * self.paslauga.kaina

    def __str__(self):
        return f"{self.uzsakymas} {self.paslauga} {self.kiekis}"

    class Meta:
        verbose_name = _("Order line")
        verbose_name_plural = _("Order lines")


class UzsakymoKomentaras(models.Model):
    uzsakymas = models.ForeignKey('Uzsakymas', on_delete=models.SET_NULL, null=True, blank=True, related_name='komentarai')
    vartotojas = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField("Data", auto_now_add=True)
    komentaras = models.TextField("Komentaras", max_length=2000)

    class Meta:
        ordering = ['-data']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nuotrauka = models.ImageField(default='default.png', upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} profilis"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.nuotrauka.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.nuotrauka.path)