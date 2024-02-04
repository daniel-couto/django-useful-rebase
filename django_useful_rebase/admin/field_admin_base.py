from django.core import exceptions
from django.utils.safestring import mark_safe

# TODO limpar import não usados em todo aplicativo
class FieldAdminBase():

    def get_fields_subset(self, admin_obj=None, excluded_fields=None):
        no_fields = []
        if admin_obj is None:
            return no_fields

        all_fields = list(set(
            [field.name for field in admin_obj.opts.local_fields] +
            [field.name for field in admin_obj.opts.local_many_to_many]
        ))
        all_fields.remove('id')
        if not excluded_fields:
            return all_fields
        else:
            result_fields = all_fields
            for f in excluded_fields:
                result_fields.remove(f)
        return result_fields

    def get_html_link(self, url, display_text=None):
        display_text = "<a href={}>{}</a>".format(url, display_text if display_text else url)
        if not display_text:
            display_text = '-'
        return mark_safe(display_text)
        
    def get_fk_value(self, fk_obj, field_name=None):
        return mark_safe(getattr(fk_obj, field_name) if field_name else str(fk_obj))

    def get_fk_change_link(self,fk_obj,field_name=None):
        return self.get_html_link(
            fk_obj.admin_change_url,
            self.get_fk_value(fk_obj, field_name))
