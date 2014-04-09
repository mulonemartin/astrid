#!/usr/bin/env python
# -*- coding: utf-8 -*-

#You don't have to do this two lines if you are using in production trought pypi.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))


from astrid.web.wsgi import WSGIApplication
from astrid.http.server import run
from astrid.web.expose import expose
from astrid.http.response import HTTPError, HTTPRedirect
from astrid.app.local import local
from astrid.html.helpers import tag
from astrid.html.forms import Form
from astrid.db.dal import Field
from astrid.html.validators import IS_INT_IN_RANGE, IS_NOT_EMPTY, \
                            IS_TIME, IS_DATE, IS_DATETIME, IS_IN_SET


from config import options


@expose(template='index.html')
def test_template():
    message = "This is a test"
    return dict(message=message)


@expose(template='index.html')
def no_template():
    message = "This is a test, no template using direct strign"
    return message


@expose()
def error():
    raise HTTPError(404, 'Un error')


@expose()
def redirect():
    raise HTTPRedirect('index')


@expose()
def session():
    local.session.set('mykey', 'value 1')
    my_value = local.session.get('mykey')
    message = "Session get 'mykey': '%s'" % my_value
    return message


@expose(template='index.html')
def html():
    ul = tag.ul()
    ul.append(tag.li('Item 1'))
    ul.append(tag.li('Item 2'))
    ul.append(tag.li('Item 3'))
    ul.append(tag.li('Item 4'))

    a = tag.a('Some link', _href='www.yahoo.com', _title='My title')
    blockquote = tag.blockquote('Some text in blockquote')
    cite = tag.cite('This is my cite')
    code = tag.code('def func(myvar):\n\tprint "melon"')
    h3 = tag.h3('Hey a title')
    p = tag.p()

    table = tag.table()
    td1 = tag.td('Col 1')
    td2 = tag.td('Col 2')
    tr = tag.tr()
    tr.append(td1)
    tr.append(td2)
    table.append(tr)

    op1 = tag.option('One',_value='one', _selected=None)
    op2 = tag.option('Two',_value='two', _selected=None)
    select = tag.select()
    select.append(op1)
    select.append(op2)

    div = tag.div()
    div.append(a)
    div.append(blockquote)
    div.append(cite)
    div.append(h3)
    div.append(code)
    div.append(p)
    div.append(table)
    div.append(ul)
    div.append(select)

    return dict(message=div)


@expose(template='index.html')
def form():
    form = Form(Field('name'), Field('age')).process()
    if form.accepted:
        print "YES"
        raise HTTPRedirect('index')

    return dict(message=form)


@expose(template='index.html')
def form2():
    form = Form(
                Field('name', requires=IS_NOT_EMPTY()),
                Field('area', 'text'),
                Field('check', 'boolean', default=True),
                Field('age', 'integer',  requires=IS_INT_IN_RANGE(1, 120), comment='Try type in a number!'),
                Field('weight', 'double'),
                Field('time', 'time', requires=IS_TIME()),
                Field('date', 'date', requires=IS_DATE(format='%Y-%m-%d')),
                Field('datetime', 'datetime', requires=IS_DATETIME(format='%Y-%m-%d %H:%M:%S')),
                Field('malefemale', 'select', length=512, label='Male/Female', requires=IS_IN_SET(['Male', 'Female'])),
                Field('multiple', 'multiple', length=512, label='Choice', requires=IS_IN_SET(['One', 'Two'])),
                Field('password', 'password'),
                Field('upload', 'upload')
            ).process()
    if form.accepted:
        raise HTTPRedirect('index')

    return dict(message=form)




if __name__ == '__main__':
    app = WSGIApplication(options)
    run(app, server=options['SERVER'], host=options['IP'], port=options['PORT'])

