from django.core import exceptions

class ValidationResult():
    is_valid = None
    has_warning = None
    info = None
    exception_type = None
    field = None
    INFO_DEFAULT = 'ERRO DESCONHECIDO'
    
    def __init__(self, is_valid, info, has_warning=False, exception_type=None, field=None):
        self.is_valid = is_valid
        self.has_warning = has_warning
        self.info = info if info else self.INFO_DEFAULT
        self.exception_type = exception_type
        self.field = field
    
    def print_safe_info(self):
        from django.utils.safestring import mark_safe
        return mark_safe(self.info)
    
    def raise_error(self):
        if self.exception_type:
            raise self.exception_type(self.print_safe_info())
        else:
            raise exceptions.ValidationError(self.print_safe_info())


class ValidatorBase():
    
    def __call__(self, model_instance=None):
        if not self.validators:
            self.validators = [m for m in dir(self.__class__) if callable(getattr(self.__class__, m)) and 'validate_' in m]
        validate_method_list = [getattr(self, m) for m in self.validators]
        results = []
        if validate_method_list:
            for method in validate_method_list:
                result = method(model_instance, (False if model_instance.pk else True))
                if result:
                    try:
                        results.extend(result)
                    except TypeError:
                        results.append(result)
        return results

    def result_creator(self, **kwargs):
        try:
            is_valid = kwargs.get('is_valid')
        except:
            is_valid = True
        
        try:
            has_warning = kwargs.get('has_warning')
        except:
            has_warning = False
        
        try:
            info = kwargs.get('info')
        except:
            info = None
        
        try:
            exception_type = kwargs.get('exception_type')
        except:
            exception_type = None
        
        try:
            field = kwargs.get('field')
        except:
            field = None
        
            
        return ValidationResult(
            is_valid=is_valid,
            has_warning=has_warning,
            info=info,
            exception_type=exception_type,
            field=field
        )