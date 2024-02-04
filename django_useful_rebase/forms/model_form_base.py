from django import forms

class ModelFormBase(forms.ModelForm):
    exceptional_edit_classes = [
        'django.forms.widgets.PermissionForm',
    ]

    just_mudanca = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea,
        label="Justificativa para alteração"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if str(self.__class__).replace("<class '","").replace("'>","") in self.exceptional_edit_classes:
        #     return
        self.block_protected_fields()
        self.block_createonly_fields()
        if self.instance.pk:
            self.set_pre_validation_msgs()
        if self.fields:
            self.block_protected_fields()
    def block_protected_fields(self):
        if not hasattr(self.instance, 'protected_fields'):
            return None
        if not self.instance.protected_fields:
            return None
        for f in self.instance.protected_fields:
            try:
                self.fields[f].disabled = True
            except KeyError :
                continue

    def block_createonly_fields(self):
        if not self.instance.pk:
            return None
        if not hasattr(self.instance, 'createonly_fields'):
            return None
        for f in self.instance.createonly_fields:
            try:
                self.fields[f].disabled = True
            except KeyError :
                continue

    def set_pre_validation_msgs(self):
        if not hasattr(self.instance, 'pre_validation_msgs'):
            return None
        results = self.instance.get_validation_results()
        if not results:
            return None

        from django.contrib import messages
        from django.utils.safestring import mark_safe
        for r in results:
            if not r.is_valid:
                try:
                    messages.error(
                        self.request, 
                        mark_safe('{}'.format(
                            r.info)))
                except AttributeError:
                    continue
            if r.has_warning:
                try:
                    messages.warning(
                        self.request, 
                        mark_safe('{}'.format(
                            r.info)))
                except AttributeError:
                    continue

    def save(self, commit=True):
        just_mudanca = self.cleaned_data.get('just_mudanca', None)

        # self.description = "my result" note that this does not work

        # Get the form instance so I can write to its fields
        instance = super().save(commit=commit)

        # this writes the processed data to the description field
        instance._change_reason = just_mudanca

        if commit:
            instance.save()

        return instance

    # def clean(self):
        # results = self.instance.get_validation_results()
        # if not results:
        #     return

        # from django.contrib import messages
        # from django.utils.safestring import mark_safe
        # for r in results:
        #     if not r.is_valid:
        #         if not r.field:
        #             messages.error(
        #                 self.request, 
        #                 mark_safe('{}'.format(
        #                     r.info)))
        #         else:
        #             self._errors[field] = self.error_class([r.info])
        #     if r.has_warning:
        #         messages.warning(
        #             self.request, 
        #             mark_safe('{}'.format(
        #                 r.info)))

        # return super().clean()
