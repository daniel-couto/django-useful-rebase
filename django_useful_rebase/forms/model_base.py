#  MODULOS PYTHON
from django.db import models
from django.core import exceptions
from django.urls import reverse
from django.utils.safestring import mark_safe
from simple_history.models import HistoricalRecords
import logging

# MODULOS DJANGO

# MODULOS DJANGO: EXTENSOES ESTRUTURANTES
from django_base.admin import FieldAdminBase
# MODULOS DJANGO: EXTENSOES

# MODULOS DO PROJETO VERDINHU - OUTROS APPS

# MODULOS DO APP ESPEFICICO



class ModelBase(models.Model):
    logger = logging.getLogger("geral")

    history = HistoricalRecords(
        inherit=True,
        history_change_reason_field=models.TextField(null=True)
    )
    
    """
    campos estritamente automaticos / calculados
    """
    automatic_strict_fields = ()
    """
    campos opcionalmente calculados / automaticos
    """
    automatic_loose_fields = ()

    """
    Campos protegidos: 
        Campos somente-leitura, nunca abertos para edição.
        Estes campos só podem ser obrigatórios combinados com métodos para gerá-los antes de salvar
        (e.g. calculados)
    """
    @property
    def protected_fields(self):
        return list(self.automatic_strict_fields)
    """
    Campos apenas-criação: 
        Campos somente-leitura aomente após criação.
        Estes campos devem ser necessariamente obrigatórios ou acompanhados de métodos para preenchimento automático
        (e.g. campos participantes de chaves)
    """
    @property
    def createonly_fields(self):
        return []

    """
    Campos obrigatórios
    """
    @property
    def required_fields(self):
        required = []
        for field in self._meta.get_fields():
            if hasattr(field, 'blank') and field.blank is False:
                required.append(field.name)
        return required


    _fields_admin = FieldAdminBase()
    
    @property
    def db_instance(self):
        try:
            return self.__class__.objects.get(pk=self.pk)
        except:
            return None
    @property
    def validator(self):
        try:
            return self._validator
        except:
            return None
    @property
    def admin_change_url(self):
        return reverse(
                'admin:{}_{}_change'.format(
                    self._meta.app_label, 
                    self._meta.model_name),
                args=(self.pk,))
    @property
    def admin_change_link(self):
        return self._fields_admin.get_html_link(self.admin_change_url, str(self))
    @property
    def all_fields(self):
        return [f.name for f in self._meta.get_fields()]
    @property
    def is_blocked(self):
        return False

    @property
    def get_govi_mapping(self):
        return None

    # def __str__(self):
    #     raise NotImplementedError
    class Meta:
        abstract=True 
    
    def get_absolute_url(self):
        return reverse('{}_detail'.format(self.__class__.__name__), kwargs={"pk": self.pk})
    def clean(self):
        self.set_automatic_strict_fields()
        self.set_automatic_loose_fields()
        if self.validator:
            for result in self.get_validation_results():
                if result and not result.is_valid:
                    raise exceptions.ValidationError(result.print_safe_info())
        super().clean()

    def save(self, *args, **kwargs):
        self.set_automatic_strict_fields()
        self.set_automatic_loose_fields()
        super().save(*args, **kwargs)

    def get_validation_results(self):
        if not self.validator:
            return None
        else:
            return self.validator(self)
    def _search_methods(self, prefix=None):
        return [getattr(self, m) for m in dir(self.__class__) if callable(getattr(self.__class__, m)) and prefix in m]
    def _execute_methods_list(self, methods=None):
        # TODO fazer o metodo identificar se são campos calculados ou derivados, e chamar com base no padrao de nome caso a lista não tenha sido informada
        if methods is None:
            return None
        for m in methods:
            m()
    def get_m2m_list(self, campo_nome=None, has_link=False, str_separator=None):
        campo = getattr(self, campo_nome)
        item_lista = campo.all()

        if not item_lista:
            return []

        if has_link:
            item_lista = [item.admin_change_link for item in item_lista]
        else:
            item_lista = [str(item) for item in item_lista]
            
        if str_separator:
            item_lista = str_separator.join([str(item) for item in item_lista])
        
        return item_lista


    def set_automatic_loose_fields(self, force=False):
        for f in self.automatic_loose_fields:
            method = getattr(self, "set_{}".format(f))
            if force:
                # se for marcado pra forçar, executa mesmo para sobrescrever o atributo
                method()
            elif not getattr(self, f):
                # executa o metodo set apenas se o atributo não estiver definido
                method()


    def set_automatic_strict_fields(self, force=False):
        for f in self.automatic_strict_fields:
            method = getattr(self, "set_{}".format(f))
            if force:
                method()
            elif (f in self.createonly_fields):
                if not getattr(self, f):
                    method()
            else:
                method()

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
    def namedtuplefetchall(self, cursor):
        "Return all rows from a cursor as a namedtuple"
        from collections import namedtuple
        
        desc = cursor.description
        nt_result = namedtuple('Result', [col[0] for col in desc])
        return [nt_result(*row) for row in cursor.fetchall()]
