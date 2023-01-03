from django.contrib import admin
from .models import (AutomobilioModelis,
                     Automobilis,
                     Paslauga,
                     Uzsakymas,
                     UzsakymoEilute,
                     UzsakymoKomentaras,
                     Profile)


class UzsakymoEiluteInline(admin.TabularInline):
    model = UzsakymoEilute
    extra = 0
    readonly_fields = ('suma',)
    fieldsets = (
        ("General", {'fields': ('paslauga', 'kiekis', 'suma')}),
    )

class UzsakymoEiluteAdmin(admin.ModelAdmin):
    model = UzsakymoEilute
    readonly_fields = ('suma',)
    fieldsets = (
        ("General", {'fields': ('paslauga', 'kiekis', 'suma')}),
    )

class UzsakymasAdmin(admin.ModelAdmin):
    list_display = ('automobilis', 'data', 'bendra')
    inlines = [UzsakymoEiluteInline]
    readonly_fields = ('bendra', 'data')

    fieldsets = (
        ("General", {'fields': ('automobilis', 'data', 'bendra')}),
    )


class AutomobilisAdmin(admin.ModelAdmin):
    list_display = ('modelis', 'valstybinis_nr', 'vin_kodas', 'kliento_vardas')
    list_filter = ('kliento_vardas', 'modelis', 'valstybinis_nr')
    search_fields = ('valstybinis_nr', 'vin_kodas', 'modelis__gamintojas', 'modelis__modelis')

class PaslaugaAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas', 'kaina')


class UzsakymoKomentarasAdmin(admin.ModelAdmin):
    list_display = ('uzsakymas', 'vartotojas', 'data', 'komentaras')


# Register your models here.
admin.site.register(AutomobilioModelis)
admin.site.register(Automobilis, AutomobilisAdmin)
admin.site.register(Paslauga, PaslaugaAdmin)
admin.site.register(Uzsakymas, UzsakymasAdmin)
admin.site.register(UzsakymoEilute, UzsakymoEiluteAdmin)
admin.site.register(UzsakymoKomentaras, UzsakymoKomentarasAdmin)
admin.site.register(Profile)