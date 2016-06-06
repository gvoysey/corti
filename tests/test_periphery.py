from hypothesis import given, settings
from hypothesis.strategies import integers


@given(integers())
@settings(max_examples=5)
def test(x):
    assert x == x
