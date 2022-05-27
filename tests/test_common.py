import pytest

from lamprey.common import format_bytes

def test_format_bytes():
    size_1 = format_bytes(866463744)
    assert 826.4 > size_1[0] > 826.3
    assert size_1[1] == 'MB'

    size_2 = format_bytes(1000000000)
    assert 953.7 > size_2[0] > 953.6
    assert size_2[1] == 'MB'

    with pytest.raises(ValueError):
        format_bytes(-1)
