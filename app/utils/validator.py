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

import bson
import types

import models

# The valid types a document ID can be.
VALID_ID_TYPES = (
    types.StringTypes,
    types.UnicodeType,
    bson.objectid.ObjectId
)


def is_valid_json(json_obj, accepted_keys):
    """Validate a JSON object from a request.

    The JSON object will also be modified based on the valid keys for the
    request being validated. All non recognized keys will be removed.

    To be invalid it either has to:
    - Be without one of the mandatory keys (for a complex validation)
    - Have no keys at the end of the validation

    :param json_obj: The JSON object to validate. It will be treated as a
                     Python dictionary.
    :param accepted_keys: A list of keys that needs to be found in the JSON
                          object.
    :return A tuple with True or False, and an optional error message.
    """
    valid_json = False
    error_message = "No valid keys defined for this request"

    if not isinstance(json_obj, types.DictionaryType):
        error_message = "Provided data is not JSON"
    else:
        if accepted_keys:
            if isinstance(accepted_keys, types.ListType):
                # Simple case, where the valid keys is just a list of keys.
                valid_json, error_message = _simple_json_validation(
                    json_obj, accepted_keys)
            elif isinstance(accepted_keys, types.DictionaryType):
                # More complex case where accepted_keys is a a dictionary with
                # mandatory and all the valid keys.
                valid_json, error_message = _complex_json_validation(
                    json_obj, accepted_keys)

    return valid_json, error_message


def _simple_json_validation(json_obj, accepted_keys):
    """Perform JSON validation with simple logic.

    The passed keys parameter is a list: if just one keys is not found,
    the JSON is not valid.

    :param json_obj: The JSON object to analyze.
    :type json_obj: dict
    :param accepted_keys: The accepted keys for this JSON object.
    :type accepted_keys: list
    :return True or False, and an error message if False.
    """
    is_valid = True
    error_message = None
    json_keys = set(json_obj.keys())

    strange_keys = json_keys - set(accepted_keys)
    if strange_keys:
        error_message = (
            "Found non recognizable keys, they will not be considered: %s" %
            ", ".join(strange_keys)
        )
        # If we have keys that are not defined in our model, remove them.
        for key in strange_keys:
            json_obj.pop(key, None)

    if not json_obj:
        # Did we remove everything from the JSON object?
        is_valid = False
        error_message = "No valid or acceptable keys in the JSON data"

    return is_valid, error_message


def _complex_json_validation(json_obj, accepted_keys):
    """Perform JSON validation with a more complex logic.

    The passed keys parameter is a dictionary that contains mandatory keys and
    all the other accepted keys.

    If one of the mandatory keys is not found, it is not valid.
    If other keys are passed and are not in the accepted keys, they will be
    discarded.

    :param json_obj: The JSON object to analyze.
    :type json_obj: dict
    :param accepted_keys: The accepted keys for this JSON object.
    :type accepted_keys: list
    :return True or False, and and error message if False or None.
    """
    is_valid = True
    error_message = None

    json_keys = set(json_obj.keys())
    mandatory_keys = set(accepted_keys.get(models.MANDATORY_KEYS))
    valid_keys = set(accepted_keys.get(models.ACCEPTED_KEYS))

    missing_keys = list(mandatory_keys - json_keys)
    if missing_keys:
        is_valid = False
        error_message = (
            "One or more mandatory keys are missing: %s" % str(missing_keys)
        )
    else:
        strange_keys = list(json_keys - valid_keys)
        if strange_keys:
            error_message = (
                "Found non recognizable keys, they will not be "
                "considered: %s" %
                ", ".join(strange_keys)
            )
            # If we have keys that are not defined in our model, remove them.
            for key in strange_keys:
                json_obj.pop(key, None)

    if not json_obj:
        # Did we remove everything from the JSON object?
        is_valid = False
        error_message = "No valid or acceptable keys in the JSON data"

    return is_valid, error_message


def is_valid_batch_json(json_obj, batch_key, accepted_keys):
    """Validates JSON object for batch operations.

    :param json_obj: The JSON object to validate.
    :type json_obj: dict
    :return True or False.
    """
    is_valid = True

    if all([json_obj, accepted_keys, batch_key]):
        if json_obj.get(batch_key, None):
            batch_op_list = json_obj.get(batch_key)

            while is_valid:
                for batch_op in batch_op_list:
                    if isinstance(batch_op, types.DictionaryType):
                        for key in batch_op.viewkeys():
                            if key not in accepted_keys:
                                is_valid &= False
                                break
                    else:
                        is_valid &= False
                        break
                break
        else:
            is_valid = False
    else:
        is_valid = False

    return is_valid


def is_valid_lab_contact_data(json_obj):
    """Validate a `contact` data structure for the Lab model.

    :param json_obj: The JSON object containing the `contact` data.
    :type json_obj: dict
    :return A tuple: True or False, and an error message if False or None.
    """
    is_valid = True
    reason = None

    contact = json_obj.get(models.CONTACT_KEY)
    if all([contact, isinstance(contact, types.DictionaryType)]):
        mandatory_keys = set(
            [models.NAME_KEY, models.SURNAME_KEY, models.EMAIL_KEY]
        )
        provided_keys = set(contact.keys())
        # Does the provided dict contain all the mandatory keys?
        if not (provided_keys >= mandatory_keys):
            missing_keys = list(mandatory_keys - provided_keys)
            is_valid = False
            reason = (
                "Missing mandatory keys for '%s' JSON object: %s" %
                (models.CONTACT_KEY, str(missing_keys))
            )
    else:
        is_valid = False
        reason = (
            "Provided '%s' data structure is not a JSON object or "
            "is empty" % models.CONTACT_KEY
        )

    return is_valid, reason


def is_valid_id(doc_id):
    """Verifies that a document id is real one.

    :param doc_id: The document id to verify.
    :type doc_id: str
    :return True or False.
    """
    is_valid = False
    if all([doc_id, isinstance(doc_id, VALID_ID_TYPES)]):
        try:
            bson.objectid.ObjectId(doc_id)
            is_valid = True
        except bson.errors.InvalidId:
            pass

    return is_valid
