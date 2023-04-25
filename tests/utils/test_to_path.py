import pytest
from pathlib import Path
from src.magmail.utils import to_path

class TestToPathFunction:
    def test_string_path(self):
        sample_path = "/magmail/tests"
        assert isinstance(to_path(sample_path), Path)

    def test_pathlib_path(self):
        sample_path = Path("/magmail/tests")
        assert isinstance(to_path(sample_path), Path)

    def test_int_value_error(self):
        test_value = 1230
        with pytest.raises(TypeError) as _e:
            to_path(test_value)

    def test_custom_type_value_error(self):
        class CustomType(): None
        test_custom_type = CustomType()

        with pytest.raises(TypeError) as _e:
            to_path(test_custom_type)
