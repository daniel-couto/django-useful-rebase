from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django_base.forms import ModelFormBase
from .field_admin_base import FieldAdminBase

class ModelAdminBase(SimpleHistoryAdmin):
    actions_on_top = True
    actions_on_bottom = True
    save_on_top = True
    view_on_site = False
    readonly_fields = ()
    createonly_fields = ()
    list_per_page = 20
    form = ModelFormBase

    def __init__(self, model, admin_site):
        self._fields_admin = FieldAdminBase()
        super().__init__(model, admin_site)
    
    def get_all_fields(self):
        return list(set( [field.name for field in self.opts.local_fields] + [field.name for field in self.opts.local_many_to_many]))

    def get_readonly_fields(self, request, obj=None):
        # criando um objeto, apenas os definidos como read_only
        if not obj:
            return self.readonly_fields
        # editando um objeto
        else:
            return self.readonly_fields + self.createonly_fields
        
    def get_fk_value(self, model_obj, field_name=None):
        return self._fields_admin.get_fk_value(model_obj, field_name)

    def get_fk_change_link(self,model_obj,field_name=None):
        return self._fields_admin.get_fk_change_link(model_obj, field_name)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            user_group = 'ADMIN'
        else:
            user_group = request.user.groups.filter(
                name__in=('CDGBA', 'CDGCE', 'CDGPE', 'CDGRS', 'CDGSP',)).first().name
            if not user_group:
                user_group = '?'

        try:
            if not obj.criador or obj.criador == '' or obj.criador is None:
                obj.criador = request.user.username
        except AttributeError:
            pass

        try:
            if not obj.criador_grupo or obj.criador_grupo == '' or obj.criador_grupo is None:
                obj.criador_grupo = user_group
        except AttributeError:
            pass

        try:
            obj.proprietario = request.user.username
            obj.user = request.user.username
        except AttributeError:
            pass

        try:
            obj.proprietario_grupo = user_group
        except AttributeError:
            pass
    
        super().save_model(request, obj, form, change)
        # super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        form.current_user = request.user
        form.admin = self
        return form


    def get_fieldsets(self, request, obj=None):
        if self.fieldsets:
            return self.fieldsets + (
                ('Controle de versão', {'fields': ('just_mudanca',)}),
            )
        else:
            return tuple(super().get_fieldsets(request, obj))


    def is_valid(self, obj):
        results = obj.get_validation_results()
        if not results:
            return True
        else:
            return False
        
    def send_result_message(self,validation_result, request):
        from django.contrib import messages
        from django.utils.safestring import mark_safe

        if not validation_result.is_valid:
            self.messages_error(
                request, 
                '{}'.format(
                    validation_result.info))
        if validation_result.has_warning:
            self.messages_warning(
                request, 
                '{}'.format(
                    validation_result.info))

    def checar_validade_registros(self,modeladmin,request,queryset):
        from django.utils.safestring import mark_safe
        from django.contrib import messages

        valid = True
        for obj in queryset:
            results = obj.get_validation_results()
            if results is not None:
                for vr in obj.get_validation_results():
                    if not vr.is_valid:
                        valid = False
                        self.messages_error(
                            request,
                            '{} :: {}'.format(obj.admin_change_link, vr.print_safe_info())
                        )
                    if vr.has_warning:
                        valid = False
                        self.messages_warning(
                            request,
                            '{} :: {}'.format(obj.admin_change_link, vr.print_safe_info())
                        )
            if valid:
                self.messages_success(
                    request,
                    '{} :: Nenhum erro encontrado'.format(obj.admin_change_link))
    checar_validade_registros.short_description = 'Validar registros'
    checar_validade_registros.allowed_permissions = ('view',)


    def update_automatic_fields(self,modeladmin,request,queryset):
        for obj in queryset:
            obj.save()
    update_automatic_fields.short_description = 'Atualizar campos automáticos'
    update_automatic_fields.allowed_permissions = ('change',)


    def force_update_automatic_fields(self,modeladmin,request,queryset):
        for obj in queryset:
            obj.set_automatic_strict_fields(force=True)
            obj.save()
    force_update_automatic_fields.short_description = 'Forçar atualização de campos automáticos'
    force_update_automatic_fields.allowed_permissions = ('change',)


    def get_actions(self, request):
        actions = super().get_actions(request)
        # if 'delete_selected' in actions:
        #     del actions['delete_selected']
        actions.update(
            {'checar_validade_registros':
                (self.checar_validade_registros,
                'checar_validade_registros',
                self.checar_validade_registros.short_description)})
        actions.update(
            {'update_automatic_fields':
                (self.update_automatic_fields,
                'update_automatic_fields',
                self.update_automatic_fields.short_description)})
        if request.user.is_superuser:
            actions.update(
                {'force_update_automatic_fields':
                    (self.force_update_automatic_fields,
                    'force_update_automatic_fields',
                    self.force_update_automatic_fields.short_description)})
        return actions


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

    def messages_debug(
        self, 
        request, 
        message, 
        extra_tags='', 
        fail_silently=False):
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        self.message_user(
            request=request, 
            message=mark_safe(message), 
            level=messages.DEBUG, 
            extra_tags=extra_tags, 
            fail_silently=fail_silently,)
    def messages_info(
        self, 
        request, 
        message, 
        extra_tags='', 
        fail_silently=False):
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        self.message_user(
            request=request, 
            message=mark_safe(message), 
            level=messages.INFO, 
            extra_tags=extra_tags, 
            fail_silently=fail_silently,)
    def messages_success(
        self, 
        request, 
        message, 
        extra_tags='', 
        fail_silently=False):
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        self.message_user(
            request=request, 
            message=mark_safe(message), 
            level=messages.SUCCESS, 
            extra_tags=extra_tags, 
            fail_silently=fail_silently,)
    def messages_warning(
        self, 
        request, 
        message, 
        extra_tags='', 
        fail_silently=False):
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        self.message_user(
            request=request, 
            message=mark_safe(message), 
            level=messages.WARNING, 
            extra_tags=extra_tags, 
            fail_silently=fail_silently,)
    def messages_error(
        self, 
        request, 
        message, 
        extra_tags='', 
        fail_silently=False):
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        self.message_user(
            request=request, 
            message=mark_safe(message), 
            level=messages.ERROR, 
            extra_tags=extra_tags, 
            fail_silently=fail_silently,)
