#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4
import hashlib

from .helpers import tag, TAG, cat
from astrid.app.local import local
from astrid.core.uuid import shrink_uuid
from astrid.core.uuid import UUID_EMPTY
from astrid.core.uuid import parse_uuid
from astrid.http.cookies import HTTPCookie
from astrid.core.collections import last_item_adapter
from astrid.http.response import HTTPJSONResponseTemplate, HTTPJSONResponse


__all__ = ['Form']


class Form(TAG):

    @staticmethod
    def widget_string(name, value, _class='string',_id=None, _class_input=''):
        return tag.input(_type='text', _name=name, _value=value or '',
                         _class=_class + ' ' + _class_input, _id=_id)

    @staticmethod
    def widget_text(name, value, _class='text', _id=None, _class_input=''):
        return tag.textarea(value or '', _name=name,
                            _class=_class + ' ' + _class_input, _id=_id, _rows=5)

    @staticmethod
    def widget_integer(name, value, _class='integer', _id=None, _class_input=''):
        return Form.widget_string(name, value, _class + ' ' + _class_input, _id)

    @staticmethod
    def widget_double(name, value, _class='double', _id=None, _class_input=''):
        return Form.widget_string(name, value, _class + ' ' + _class_input, _id)

    @staticmethod
    def widget_date(name, value, _class='date', _id=None, _class_input=''):
        return Form.widget_string(name, value, _class + ' ' + _class_input, _id)

    @staticmethod
    def widget_time(name, value, _class='time', _id=None, _class_input=''):
        return Form.widget_string(name, value, _class + ' ' + _class_input, _id)

    @staticmethod
    def widget_datetime(name, value, _class='datetime', _id=None, _class_input=''):
        return Form.widget_string(name, value, _class + ' ' + _class_input, _id)

    @staticmethod
    def widget_password(name, value, _class='password', _id=None, _class_input=''):
        return tag.input(_type='password', _name=name, _value=value or '',
                         _class=_class + ' ' + _class_input, _id=_id)

    @staticmethod
    def widget_upload(name, value, _class='file', _id=None, _class_input=''):
        return tag.input(_type='file', _name=name, _value=value or '',
                         _class=_class + ' ' + _class_input, _id=_id)

    @staticmethod
    def widget_boolean(name,value,_class='boolean',_id=None, _class_input=''):
        return tag.input(_type='checkbox',_name=name,_value='t',
                         _checked='checked' if value else None,
                         _class=_class + ' ' + _class_input,_id=_id)

    @staticmethod
    def widget_select(name, value, options, zero, _class='', _id=None, _class_input=''):
        def selected(k): 'selected' if str(value) == str(k) else None
        select_tag = tag.select(_name=name, _class=_class + ' ' + _class_input, _id=_id)
        for k, n in options:
            if not k or k == '':
                if zero is None:
                    continue

            if str(value) == str(k):
                select_tag.append(tag.option(n, _value=k, _selected=''))
            else:
                select_tag.append(tag.option(n, _value=k))
        return select_tag

    @staticmethod
    def widget_select_group(name, value, options, zero, _class='', _id=None, _class_input=''):        
        select_tag = tag.select(_name=name, _class=_class + ' ' + _class_input, _id=_id)
        for group_key, group_value in options.iteritems():
            optgrp = tag.optgroup(_label=group_key)
            for item_id, item_text in group_value:
                if str(value) == str(item_id):
                    optgrp.append(tag.option(item_text, _value=item_id, _selected=''))
                else:
                    optgrp.append(tag.option(item_text, _value=item_id))
            select_tag.append(optgrp)
            
        return select_tag

    @staticmethod
    def widget_dynamic(name, value, options, zero, _class='', _id=None, _class_input=''):
        def selected(k): 'selected' if str(value) == str(k) else None
        select_tag = tag.select(_name=name, _class=_class + ' ' + _class_input, _id=_id)
        for k, n in options:
            if not k or k == '':
                if zero is None:
                    continue

            if str(value) == str(k):
                select_tag.append(tag.option(n, _value=k, _selected=''))
            else:
                select_tag.append(tag.option(n, _value=k))

        if value:
            select_tag.append(tag.option('(seleccionado oculto)', _value=value, _selected=''))

        return select_tag

    @staticmethod
    def widget_radio(name, value, options, zero, _class='', _id=None, _class_input=''):
        div_tag = []
        for k, n in options:
            if not k or k == '':
                continue
            label = tag.label(_class='radio')
            if value == k:
                label.append(tag.input(_type='radio', _name=name, _value=k, _checked='', _id=_id))
            else:
                label.append(tag.input(_type='radio', _name=name, _value=k, _id=_id))
            label.append(n)
            div_tag.append(label)
        return ''.join([str(item) for item in div_tag])

    @staticmethod
    def widget_multiple(name, values, options, zero, _class='', _id=None, _class_input=''):
        values = values or []
        #def selected(k): 'selected' if k in values else None
        def selected(k):
            if str(k) in values:
                return 'selected'
            else:
                return None

            #'selected' if str(k) in values else None
        select_tag = tag.select(_name=name, _class=_class + ' ' + _class_input,
                                _multiple='multiple', _id=name)
        for k, n in options:
            select_tag.append(tag.option(n, _value=k, _selected=selected(k)))
        return select_tag

    @staticmethod
    def widget_hidden(name, value, _class='hidden', _id=None):
        return tag.input(_type='hidden', _name=name, _value=value or '',
                         _class=_class, _id=_id)

    @staticmethod
    def widget_upload_custom(name, value, _class='file', _id=None, _class_input=''):
        return tag.input(_type='file', _name=name, _value=value or '',
                         _class=_class + ' ' + _class_input, _id=_id, _onchange="handleFiles(this.files)")

    @staticmethod
    def widget_autocomplete(name, value, options, _class='string', _id=None, _class_input=''):
        """
        <input type="text" class="span6 m-wrap" style="margin: 0 auto;" data-provide="typeahead" data-items="4"
        data-source="[&quot;Alabama&quot;,&quot;Alaska&quot;,&quot;Arizona&quot;,&quot;Arkansas&quot;
        ,&quot;California&quot;,&quot;Colorado&quot;,&quot;Connecticut&quot;,&quot;Delaware&quot;,
        &quot;Florida&quot;,&quot;Georgia&quot;,&quot;Hawaii&quot;,&quot;Idaho&quot;,&quot;Illinois&quot;,
        &quot;Indiana&quot;,&quot;Iowa&quot;,&quot;Kansas&quot;,&quot;Kentucky&quot;,&quot;Louisiana&quot;,
        &quot;Maine&quot;,&quot;Maryland&quot;,&quot;Massachusetts&quot;,&quot;Michigan&quot;,
        &quot;Minnesota&quot;,&quot;Mississippi&quot;,&quot;Missouri&quot;,&quot;Montana&quot;,
        &quot;Nebraska&quot;,&quot;Nevada&quot;,&quot;New Hampshire&quot;,&quot;New Jersey&quot;,
        &quot;New Mexico&quot;,&quot;New York&quot;,&quot;North Dakota&quot;,&quot;North Carolina&quot;,
        &quot;Ohio&quot;,&quot;Oklahoma&quot;,&quot;Oregon&quot;,&quot;Pennsylvania&quot;,&quot;Rhode Island&quot;,
        &quot;South Carolina&quot;,&quot;South Dakota&quot;,&quot;Tennessee&quot;,&quot;Texas&quot;,&quot;Utah&quot;,
        &quot;Vermont&quot;,&quot;Virginia&quot;,&quot;Washington&quot;,&quot;West Virginia&quot;,
        &quot;Wisconsin&quot;,&quot;Wyoming&quot;]" />
        """
        input = tag.input(_type='text', _name=name ,_value=value or '', _class=_class + ' ' + _class_input, _id=_id)
        input.attributes['_data-provide'] = "typeahead"
        input.attributes['_data-items'] = "4"
        data = ['"%s"' % k for k,n in options]
        input.attributes['_data-source'] = '[%s]' % ','.join(data)

        return input

    def __init__(self, *fields, **attributes):
        attributes['_action'] = attributes.get('_action', '')
        attributes['_method'] = attributes.get('_method', 'POST')
        attributes['_enctype'] = attributes.get('_enctype', 'multipart/form-data')
        attributes['submit'] = attributes.get('submit', 'Submit')
        attributes['formstyle'] = attributes.get('formstyle', Form.style_bootstrap)
        self.ui = attributes.get('ui', {})
        self.attributes = attributes
        self.fields = fields
        self.errors = {}
        self.vars = {}
        self.input_vars = None
        self.processed = False
        self.submitted = False
        self.accepted = False
        self.valid_xsrf = False
        self.valid_resub = False
        self.id_prefix = attributes.get('_id_prefix', '')
        self.formname = 'form-'+hashlib.md5(
            ''.join(f.name for f in fields)).hexdigest()
        self.formkey_xsrf = None
        self.formkey_resub = None
        self.custom_elements = {}
        self.enabled_xsrf = True

    def process(self, vars=None, keepvalues=False):

        if not self.processed:
            self.processed = True

            if vars is not None:
                self.input_vars = vars
            elif local.request.method == 'GET':
                self.input_vars = local.request.query
            elif local.request.method == 'POST':
                self.input_vars = local.request.form

            if local.request.method == 'GET':
                self.setxsrf_token()

            elif local.request.method == 'POST':
                # CSRF validation
                if self.validate_xsrf_token():
                    self.valid_xsrf = True

                # We have to generate a new token                
                self.setxsrf_token()                
                
                # validate input
                if self.valid_xsrf:                    
                    self.submitted = True
                    for field in self.fields:
                        value = self.input_vars.get(field.name)
                        if isinstance(value, list) and len(value) == 1:
                            value = value[0]
                        value, error = field.validate(value)
                        if error:
                            self.errors[field.name] = error
                        else:
                            self.vars[field.name] = value

                    #Esto hacemos para agregar los hidden a los form vars
                    for key, h_value in self.attributes.get('hidden', {}).iteritems():
                        self.vars[key] = h_value

                    if not self.errors:
                        self.accepted = True

        # reset default values in form
        if not self.submitted or self.accepted and not keepvalues:
            if not self.input_vars:
                self.input_vars = dict()

            for field in self.fields:
                self.input_vars[field.name] = field.default

        return self

    @staticmethod
    def get_field_widget(form, field, name, value, id, _class_input=''):
        if field.widget:
            input = field.widget(name, value, _id=id, _class_input=_class_input)
        else:
            # special treatment to selects, cause requires options            
            if field.type in ['select', 'select_group', 'multiple', 'radio', 'autocomplete', 'dynamic']:
                requires = field.requires
                if not isinstance(requires, (list, tuple)):
                    requires = [requires]
                if requires:
                    if hasattr(requires[0], 'options'):
                        options = requires[0].options()
                        zero = requires[0].zero
                    else:
                        raise SyntaxError(
                            'widget cannot determine options of %s' % field)
                input = getattr(form, 'widget_'+field.type)(name, value, options, zero,  _id=id, _class_input=_class_input)
            else:
                input = getattr(form, 'widget_'+field.type)(name, value, _id=id, _class_input=_class_input)
        return input

    @staticmethod
    def style_bootstrap(form):
        fieldset = tag.fieldset()
        attr = form.attributes
        for field in form.fields:
            name = field.name
            id = form.id_prefix + name
            #if field.type in ['hidden']:
            #    continue  # Hidden field = No render
            label = tag.label(field.label,_for=id,_class='control-label')
            value = form.input_vars.get(name)
            if field.type not in ['multiple'] and isinstance(value, list):
                value = value[0]
            widget = form.get_field_widget(form, field, name, value, id, _class_input=form.ui.get('input_class', ''))
            wrapper = tag.div(widget,_class='controls')
            if name in form.errors:
                wrapper.append(tag.div(form.errors[name], _class='error-block'))
            if field.comment:
                wrapper.append(tag.span(field.comment,_class='help-inline'))
            fieldset.append(tag.div(label,wrapper,_class='control-group'))
        submit = tag.button(attr['submit'], _type='submit',
                            _class='btn btn-primary')
        #reset = tag.button('Reset', _type='reset', _class='btn')
        fieldset.append(tag.div(submit, _class='form-actions'))
        if form.formkey_xsrf:
            fieldset.append(tag.input(_name='xsrf-'+form.formname,_type='hidden',
                                      _value=form.formkey_xsrf))
        if form.formkey_resub:
            fieldset.append(tag.input(_name='resub-'+form.formname,_type='hidden',
                _value=form.formkey_resub))
        for key, value in attr.get('hidden',{}).iteritems():
            fieldset.append(tag.input(_name=key,_type='hidden',_value=value))
        attr['_class'] = attr.get('_class','form-horizontal')
        return tag.form(fieldset, **attr)

    def custom(self, ui=None):
        attr = self.attributes

        if not ui:
            ui = dict(
                label_class='control-label',
                input_class='',
                error_class='error-block',
                comment_class='help-inline',
                submit_class='btn btn-primary'
            )

        for field in self.fields:
            name = field.name
            id = self.id_prefix + name
            label = tag.label(field.label, _for=id,_class=ui.get('label_class', 'control-label'))
            value = self.input_vars.get(name)
            if field.type not in ['multiple'] and isinstance(value, list):
                value = value[0]
            widget = self.get_field_widget(self, field, name, value, id, _class_input=ui.get('input_class', ''))

            self.custom_elements[id] = {}
            self.custom_elements[id]['label'] = label
            self.custom_elements[id]['widget'] = widget

            if name in self.errors:                
                self.custom_elements[id]['error'] = tag.div(self.errors[name],
                                                            _class=ui.get('error_class', 'error-block'))
            else:
                self.custom_elements[id]['error'] = ''

            if field.comment:
                self.custom_elements[id]['comment'] = tag.span(field.comment,
                                                            _class=ui.get('comment_class', 'help-inline'))
            else:
                self.custom_elements[id]['comment'] = ''


        submit = tag.button(attr['submit'], _type='submit',
                        _class=ui.get('submit_class', 'btn btn-primary'))
        self.custom_elements['_submit'] = submit
        
        if self.formkey_xsrf:
            self.custom_elements['_xsrf'] = tag.input(_name='xsrf-'+self.formname, _type='hidden',
                                                        _value=self.formkey_xsrf)
        else:
            self.custom_elements['_xsrf'] = ''

        if self.formkey_resub:
            self.custom_elements['_resub'] = tag.input(_name='resub-'+self.formname, _type='hidden',
                                                            _value=self.formkey_resub)
        else:
            self.custom_elements['_resub'] = ''

        hiddens = tag.div()
        hidden_items = False
        for key, value in attr.get('hidden', {}).iteritems():
            hidden_items = True
            hiddens.append(tag.input(_name=key, _type='hidden',_value=value))

        if hidden_items:
            self.custom_elements['hiddens'] = hiddens
        else:
            self.custom_elements['hiddens'] = ''

        attr = self.attributes

        self.custom_elements['form_begin'] = '<form action="" class="%(class)s" enctype="%(enc_type)s" id="%(id)s" method="POST">' % \
                                             {'class': attr.get('_class','form-horizontal'),
                                              'id': attr.get('_id','form-'),
                                              'enc_type': attr.get('_enctype','multipart/form-data')}
        self.custom_elements['form_end'] = '%(xsrf)s%(resub)s%(hiddens)s</form>' % {'xsrf': self.custom_elements['_xsrf'],
                                                                         'resub': self.custom_elements['_resub'],
                                                                         'hiddens': self.custom_elements['hiddens']}

    def xml(self):
        return self.attributes['formstyle'](self).xml()

    def ajax(self, path_template='', error_text='Errors in forms', cookies=None):

        if local.request.method == 'GET':
            raise HTTPJSONResponseTemplate({'status': 'ok'}, 
                                            dict(form=self), 
                                            path_template=path_template, 
                                            status_code=200,
                                            cookies=cookies)
        elif local.request.method == 'POST':

            if self.enabled_xsrf and not self.valid_xsrf:
                json_response = dict(
                        error_text = 'CSRF validation fail! Try loading the form again!',
                        error_form = self.errors
                    )
                raise HTTPJSONResponseTemplate(json_response, 
                                            dict(form=self), 
                                            path_template=path_template, 
                                            status_code=400,
                                            cookies=cookies)
            if self.errors:                
                json_response = dict(
                    error_text = error_text,
                    error_form = self.errors
                )
                raise HTTPJSONResponseTemplate(json_response, 
                                            dict(form=self), 
                                            path_template=path_template, 
                                            status_code=400,
                                            cookies=cookies)
            else:
                raise HTTPJSONResponseTemplate({'status': 'ok'}, 
                                            dict(form=self), 
                                            path_template=path_template, 
                                            status_code=200,
                                            cookies=cookies)
        else:
            raise HTTPJSONResponse('HTTP METHOD NOT SUPPORTED', 400)

    def getxsrf_token(self):

        if self.formkey_xsrf:
            return self.formkey_xsrf

        cookies = local.request.cookies

        form_name = 'xsrf-' + self.formname

        if form_name in cookies:
            xsrf_token = cookies[form_name]
        else:
            xsrf_token = self.setxsrf_token()
        
        self.formkey_xsrf = xsrf_token
        return xsrf_token

    def setxsrf_token(self):

        options = local.options
        response = local.response
        request = local.request

        form_name = 'xsrf-' + self.formname

        xsrf_token = shrink_uuid(uuid4())        
        response.cookies.append(HTTPCookie(
                                form_name,
                                value=xsrf_token,
                                path=request.root_path,
                                httponly=True,
                                options=options))

        self.formkey_xsrf = xsrf_token

        return xsrf_token

    def delxsrf_token(self):

        options = local.options
        response = local.response
        request = local.request

        self.formkey_xsrf = None
        form_name = 'xsrf-' + self.formname

        response.cookies.append(HTTPCookie.delete(
            form_name,
            path=request.root_path,
            options=options))

    def validate_xsrf_token(self):

        form = local.request.form
        form_name = 'xsrf-' + self.formname

        if form_name in form:
            xsrf_token_form = form[form_name][-1]
            xsrf_token_cookie = self.getxsrf_token()
            
            return xsrf_token_form == xsrf_token_cookie\
                   and parse_uuid(xsrf_token_form) != UUID_EMPTY
        else:
            self.delxsrf_token()
            return False