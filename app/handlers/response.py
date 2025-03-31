# Copyright (C) Linaro Limited 2014,2015
# Author: Milo Casagrande <milo.casagrande@linaro.org>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""A generic response object that handlers can pass along."""

import pymongo.cursor
import types


class HandlerResponse(object):
    """A custom response object that handlers should use to communicate.

    This has to be used to pass custom reason or set custom headers after
    an action has been performed.

    The result of the action must be stored in the object `result` attribute.
    This attribute will always be a list.

    `count` and `limit` should be stored in their own attributes as well.
    By default they are set to None and will not be included in the
    serializable view.

    To send this response on the wire, serialize the object by calling
    `to_dict()` or `repr`. They will return a dictionary view of the object.
    """
    def __init__(self, status_code=200):
        """Create a new HandlerResponse.

        By default the status code is set to 200.
        """
        if not isinstance(status_code, types.IntType):
            raise ValueError("Value must be an integer")

        self._status_code = status_code
        self._count = None
        self._errors = []
        self._headers = None
        self._limit = None
        self._messages = []
        self._reason = None
        self._result = None
        self._skip = None

    @property
    def status_code(self):
        """The response status code."""
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        """The response status code.

        :param value: The status code, must be an int.
        """
        if not isinstance(value, types.IntType):
            raise ValueError("Value must be an integer")

        self._status_code = value

    @property
    def reason(self):
        """The response reason."""
        return self._reason

    @reason.setter
    def reason(self, value):
        """The response reason.

        :param value: The reason as string.
        """
        if not isinstance(value, types.StringTypes):
            raise ValueError("Value must be a string")

        self._reason = value

    @property
    def headers(self):
        """The custom headers for this response."""
        return self._headers

    @headers.setter
    def headers(self, value):
        """The headers that should be added to this response.

        :param value: A dictionary with the headers to set.
        """
        if not isinstance(value, types.DictionaryType):
            raise ValueError("Value must be a dictionary")

        self._headers = value

    @property
    def count(self):
        """How many results are included."""
        return self._count

    @count.setter
    def count(self, value):
        """Set the number of results included.
        If set to None, it will not be displayed in the output.

        :param value: The number of total results.
        """
        if any([value is None, isinstance(value, types.IntType)]):
            self._count = value
        else:
            raise ValueError("Value must be a integer")

    @property
    def limit(self):
        """The number of results requested."""
        return self._limit

    @limit.setter
    def limit(self, value):
        """Set the number of results requested.
        If set to None, it will not be displayed in the output.

        :param value: The number of requested results.
        """
        if any([value is None, isinstance(value, types.IntType)]):
            self._limit = value
        else:
            raise ValueError("Value must be an integer")

    @property
    def skip(self):
        """The number of results skipped."""
        return self._skip

    @skip.setter
    def skip(self, value):
        """Set the number of skipped values.
        If set to None, it will not be displayed in the output.

        :param value: The number of skipped values.
        """
        if any([value is None, isinstance(value, types.IntType)]):
            self._skip = value
        else:
            raise ValueError("Value must be an integer")

    @property
    def result(self):
        """The result associated with this response.

        :return A list containing the results or None if specifically set to.
        """
        return self._result

    @result.setter
    def result(self, value):
        """Set the result value.

        It can be set to None to control the `to_dict()` method and its output.
        If set to None, it will not be included in the dictionary view of the
        object.

        All passed values, if not of type list, will be wrapped around a list.
        """
        if value is None:
            self._result = value
        else:
            # The pymongo cursor is an iterable.
            if not isinstance(value, (types.ListType, pymongo.cursor.Cursor)):
                value = [value]
            elif isinstance(value, pymongo.cursor.Cursor):
                value = [r for r in value]
            self._result = value

    @property
    def errors(self):
        """The errors that this response might have."""
        return self._errors

    @errors.setter
    def errors(self, value):
        """Set the errors of this response."""
        if value:
            if isinstance(value, types.ListType):
                self._errors.extend(value)
            else:
                self._errors.append(value)

    @property
    def messages(self):
        """The response messages."""
        return self._messages

    @messages.setter
    def messages(self, value):
        """Set the messages for this response."""
        if value:
            if isinstance(value, types.ListType):
                self._messages.extend(value)
            else:
                self._messages.append(value)

    def to_dict(self):
        """Create a view of this object as a dictionary.

        The `headers` property is not included.

        :return The object as a dictionary.
        """
        dict_obj = {}

        dict_obj["code"] = self.status_code

        if self.count is not None:
            dict_obj["count"] = self.count

        if self.limit is not None:
            dict_obj["limit"] = self.limit

        if self.skip is not None:
            dict_obj["skip"] = self.skip

        if self.result is not None:
            dict_obj["result"] = self.result

        if self.reason is not None:
            dict_obj["reason"] = self.reason

        if self.errors:
            dict_obj["errors"] = self.errors

        if self.messages:
            dict_obj["messages"] = self.messages

        return dict_obj

    def __repr__(self):
        return self.to_dict()
