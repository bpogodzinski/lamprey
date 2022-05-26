from lamprey.common import format_bytes

def test_format_bytes():
    assert format_bytes(866463744) == (826.32421875, 'MB')