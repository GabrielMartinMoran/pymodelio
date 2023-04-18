from pymodelio.undefined import Undefined


def test_repr_returns_string_representation_of_undefined():
    undefined = Undefined()
    assert str(undefined) == '<pymodelio.UNDEFINED>'
