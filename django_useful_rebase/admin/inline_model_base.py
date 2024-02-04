from django.contrib import admin
from django.urls import reverse, resolve
from .field_admin_base import FieldAdminBase
from django.utils.safestring import mark_safe


class TabularInlineBase(admin.TabularInline):
    extra = 0
    view_on_site = False
    show_change_link = True
    readonly_fields = ()
    createonly_fields = ()
    add_permission = False
    delete_permission = False
    change_permission = False

    def has_add_permission(self, request, obj=None):
        return self.add_permission

    def has_delete_permission(self, request, obj=None):
        return self.delete_permission

    def has_change_permission(self, request, obj=None):
        return self.change_permission

    # TODO replicar funções get_relation_field_* para AdminModelBase ou mover para FieldAdminBase e configurar para TabularInlineBase e AdminModelBase usarem elas.
    # TODO varrer o código em busca de outros locais que usam metodos antigos para obter links
    # TODO se model for do tipo m2m (through), fazer o django ignorar os erros de campos inexistentes em readonly_fiels e buscar eles baseados nas colunas do modelo e das suas foreignkeys (observação, criar o campo "relation_model" ou deduzir ele no código a partir do valor do campo model)
    # TODO mudar esse metodo pra classe admin field, que deve incluida como atributo de validator e inline
    # TODO tentar criar um composite aqui em que fieldAdminBase seja um campo de field
        
    def get_fk_value(self, model_obj, field_name=None):
        return self._fields_admin.get_fk_value(model_obj, field_name)

    def get_fk_change_link(self,model_obj,field_name=None):
        return self._fields_admin.get_fk_change_link(model_obj, field_name)

    def __init__(self, *args, **kwargs):
        self._fields_admin = FieldAdminBase()
        super().__init__(*args, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super().get_formset(request, obj, **kwargs)
        


    def mask_percent(self, value, is_centesimal=True):
        if not value:
            value = 0
        elif is_centesimal:
            value = value*100
        return '{0:.2f}%'.format(value)
    def mask_money(self, value):
        if not value:
            value = 0
        return 'R${0:.2f}'.format(value)
    def mask_minutes(self, value):
        if not value:
            value = 0
        return '{0} min'.format(value)
