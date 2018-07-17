#! /usr/bin/env python
"""
Unit tests for landlab.model_parameter_dictionary
"""
import pytest
from nose.tools import with_setup
import os
import tempfile
import numpy as np

from landlab import ModelParameterDictionary
from landlab.core.model_parameter_dictionary import MissingKeyError, ParameterValueError


def test_read_file(pdict_setup):
    all_keys = set(
        ["FLOAT_VAL", "INT_VAL", "STRING_VAL", "TRUE_BOOL_VAL", "FALSE_BOOL_VAL"]
    )
    param_list = set(pdict_setup.param_dict.params())

    assert param_list == all_keys


def test_read_file_name(pdict_setup):
    (prm_fd, prm_file_name) = tempfile.mkstemp()

    prm_file = os.fdopen(prm_fd, "w")
    prm_file.write(pdict_setup.param_dict_file)
    prm_file.close()

    param_dict = ModelParameterDictionary()
    param_dict.read_from_file(prm_file_name)

    os.remove(prm_file_name)

    all_keys = set(
        ["FLOAT_VAL", "INT_VAL", "STRING_VAL", "TRUE_BOOL_VAL", "FALSE_BOOL_VAL"]
    )
    param_list = set(param_dict.params())

    assert param_list == all_keys


def test_read_file_like_twice(pdict_setup):
    from six import StringIO

    param_file = StringIO(pdict_setup.param_dict_file)
    param_dict_1 = ModelParameterDictionary()
    param_dict_2 = ModelParameterDictionary()

    param_dict_1.read_from_file(param_file)
    param_dict_2.read_from_file(param_file)


def test_read_int(pdict_setup):
    assert pdict_setup.param_dict.read_int("INT_VAL") == 1

    with pytest.raises(ParameterValueError):
        pdict_setup.param_dict.read_int("FLOAT_VAL")

    with pytest.raises(MissingKeyError):
        pdict_setup.param_dict.read_int("MISSING_INT")

    assert pdict_setup.param_dict.read_int("MISSING_INT", 2) == 2


def test_get_int(pdict_setup):
    assert pdict_setup.param_dict.get("INT_VAL", ptype=int) == 1

    with pytest.raises(ParameterValueError):
        pdict_setup.param_dict.get("FLOAT_VAL", ptype=int)

    with pytest.raises(MissingKeyError):
        pdict_setup.param_dict.get("MISSING_INT", ptype=int)


def test_set_default(pdict_setup):
    pdict_setup.param_dict.setdefault("MISSING_INT", 2)
    assert pdict_setup.param_dict.read_int("MISSING_INT") == 2


def test_read_float(pdict_setup):
    assert pdict_setup.param_dict.read_float("FLOAT_VAL") == 2.2
    assert pdict_setup.param_dict.read_float("INT_VAL") == 1

    with pytest.raises(ParameterValueError):
        pdict_setup.param_dict.read_float("STRING_VAL")

    with pytest.raises(MissingKeyError):
        pdict_setup.param_dict.read_float("MISSING_FLOAT")


def test_read_string(pdict_setup):
    assert pdict_setup.param_dict.read_string("STRING_VAL") == "The Landlab"
    assert pdict_setup.param_dict.read_string("INT_VAL") == "1"
    assert pdict_setup.param_dict.read_string("FLOAT_VAL") == "2.2"

    with pytest.raises(MissingKeyError):
        pdict_setup.param_dict.read_string("MISSING_STRING")


def test_read_bool(pdict_setup):
    assert pdict_setup.param_dict.read_bool("TRUE_BOOL_VAL") == True
    assert pdict_setup.param_dict.read_bool("FALSE_BOOL_VAL") == False

    with pytest.raises(MissingKeyError):
        pdict_setup.param_dict.read_bool("MISSING_BOOLEAN")

    with pytest.raises(ParameterValueError):
        pdict_setup.param_dict.read_bool("STRING_VAL")


def test_dict_keys(pdict_setup):
    all_keys = set(
        ["FLOAT_VAL", "INT_VAL", "STRING_VAL", "TRUE_BOOL_VAL", "FALSE_BOOL_VAL"]
    )
    assert set(pdict_setup.param_dict) == all_keys
    for key in all_keys:
        assert key in pdict_setup.param_dict


def test_dict_index(pdict_setup):
    assert pdict_setup.param_dict["INT_VAL"] == "1"


def setup_auto_type():
    from six import StringIO

    _TEST_FILE = u"""
# A Comment
INT_VAL:
1
DBL_VAL:
1.2
STR_VAL:
landlab
BOOL_VAL:
true
INT_ARRAY_VAL:
1,2 ,4 ,7

DBL_ARRAY_VAL:
1.,2. ,4. ,7.
    """
    param_dict = ModelParameterDictionary(
        auto_type=True, from_file=StringIO(_TEST_FILE)
    )
    globals().update({"param_dict": param_dict})


@with_setup(setup_auto_type)
def test_auto_type():
    assert param_dict["INT_VAL"] == 1
    assert param_dict["DBL_VAL"] == 1.2
    assert param_dict["STR_VAL"] == "landlab"
    assert param_dict["BOOL_VAL"] == True


@with_setup(setup_auto_type)
def test_int_vector():
    val = param_dict["INT_ARRAY_VAL"]

    assert list(val) == [1, 2, 4, 7]
    assert isinstance(val, np.ndarray)
    assert val.dtype == np.int


@with_setup(setup_auto_type)
def test_float_vector():
    val = param_dict["DBL_ARRAY_VAL"]

    assert list(val) == [1., 2., 4., 7.]
    assert isinstance(val, np.ndarray)
    assert val.dtype == np.float
