from django.contrib import admin

from test_weenat.models import DataRecord, Datalogger, Location, Measurement


class DataRecordInline(admin.TabularInline):
    model = DataRecord

class DataloggerAdmin(admin.ModelAdmin):
    list_display = ('id',)
    inlines = [DataRecordInline]

# Admin for Location
class LocationAdmin(admin.ModelAdmin):
    list_display = ('lat', 'lng', 'get_datalogger', 'get_datarecord')

    def get_datalogger(self, obj):
        return obj.datarecord_set.first().datalogger.id if obj.datarecord_set.exists() else None
    get_datalogger.short_description = 'Datalogger'

    def get_datarecord(self, obj):
        return obj.datarecord_set.first().id if obj.datarecord_set.exists() else None
    get_datarecord.short_description = 'DataRecord'

# Admin for Measurement
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'get_datalogger', 'get_datarecord')

    def get_datalogger(self, obj):
        return obj.datarecord_set.first().datalogger.id if obj.datarecord_set.exists() else None
    get_datalogger.short_description = 'Datalogger'

    def get_datarecord(self, obj):
        return obj.datarecord_set.first().id if obj.datarecord_set.exists() else None
    get_datarecord.short_description = 'DataRecord'


# Admin for DataRecord
class DataRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'at', 'datalogger')
    list_filter = ('at',)
    search_fields = ('datalogger__id',)


admin.site.register(Datalogger, DataloggerAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DataRecord, DataRecordAdmin)
