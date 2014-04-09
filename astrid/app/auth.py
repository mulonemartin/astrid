#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Account(object):
    """ Container of user specific security information   """

    def __init__(self,
                 id='',
                 first_name='',
                 last_name='',
                 username='',
                 email='',
                 alias='',
                 roles=[],
                 ticket=''):
        """ User specific """

        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.alias = alias
        self.roles = roles
        self.ticket = ticket

    def dump(self):
        """ Convert to string to encoded separated by '\x1f' """
        return '\x1f'.join([
            self.id,
            self.first_name,
            self.last_name,
            self.username,
            self.email,
            self.alias,
            ';'.join(self.roles),
            self.ticket])

    @classmethod
    def load(cls, s):
        """ Load converted """
        acc_list = s.split('\x1f', 3)

        return cls(id=acc_list[0],
                    fist_name=acc_list[1],
                    last_name=acc_list[2],
                    username = acc_list[3],
                    email = acc_list[4],
                    alias = acc_list[5],
                    roles = acc_list[6].split(';'),
                    ticket = acc_list[7])
