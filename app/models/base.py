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

"""The base document abstract model that represents a mongodb document."""

import abc


# pylint: disable=abstract-class-not-used
class BaseDocument(object):
    """The base document abstract model for all other documents.

    It defines the necessary methods and properties that all documents must
    implement.
    """

    __metaclass__ = abc.ABCMeta

    id_doc = (
        """
        The ID of this document as returned by mongodb.

        This should only be set with values returned by mongodb since it is
        an internal used field.
        """
    )

    # pylint: disable=invalid-name
    id = abc.abstractproperty(None, None, doc=id_doc)

    @abc.abstractproperty
    def collection(self):
        """The collection this document belongs to."""
        return None

    created_on_doc = (
        """
        The date this document was created.

        A datetime object with UTC time zone.
        """
    )

    created_on = abc.abstractproperty(None, None, doc=created_on_doc)

    version_doc = (
        """
        The schema version number of this object.
        """
    )

    version = abc.abstractproperty(None, None, doc=version_doc)

    @abc.abstractmethod
    def to_dict(self):
        """Return a dictionary view of the document that can be serialized."""
        raise NotImplementedError(
            "Class '%s' doesn't implement to_dict()" % self.__class__.__name__
        )

    @staticmethod
    @abc.abstractmethod
    def from_json(json_obj):
        """Build a document from a JSON object.

        The passed `json_obj` must be a valid Python dictionary. No checks are
        performed on its type.

        :param json_obj: The JSON object from which to build this object.
        :type json_obj: dict
        """
        raise NotImplementedError("This class doesn't implement from_json()")
