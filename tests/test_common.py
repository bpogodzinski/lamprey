import pytest

from lamprey.common import format_bytes

def test_format_bytes():
    size, postfix = format_bytes(866463744)
    assert 826.4 > size > 826.3
    assert postfix == 'MB'

    size, postfix = format_bytes(1000000000)
    assert 953.7 > size > 953.6
    assert postfix == 'MB'

    size, postfix = format_bytes(1)
    assert size == 1
    assert postfix == ''

    with pytest.raises(ValueError):
        format_bytes(-1)
