import re

from ams2_ai.identity.romanize import romanize_name

ASCII_NAME = re.compile(r"^[\x20-\x7E]*$")


def test_romanize_chinese_name():
    assert romanize_name("李华") == "Li Hua"


def test_romanize_accented_latin():
    assert romanize_name("José García") == "Jose Garcia"


def test_romanize_preserves_plain_latin():
    assert romanize_name("Michael Schumacher") == "Michael Schumacher"


def test_romanize_output_is_ascii():
    for sample in ("李华", "田中太郎", "Müller", "François"):
        assert ASCII_NAME.match(romanize_name(sample))
