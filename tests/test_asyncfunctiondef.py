from textwrap import dedent

from ensure_trailing_commas.trailing_comma_finder import find_missing_trailing_commas


def test_functiondef():
    assert find_missing_trailing_commas(dedent("""
        async def test(
            a
        ): pass
    """)) == [22]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            param=value
        ): pass
    """)) == [32]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            *args
        ): pass
    """)) == [26]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            param=value
        ): pass
    """)) == [39]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *,
            param=value
        ): pass
    """)) == [46]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            *,
            param=value
        ): pass
    """)) == [39]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *args,
            param=value
        ): pass
    """)) == [50]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *args,
            param=value,
            **kwargs
        ): pass
    """)) == [64]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *args,
            param=value,
            **kwargs  # comment
        ): pass
    """)) == [64]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a=((),(),())
        ): pass
    """)) == [33]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a=b() + c(1) + d()
        ): pass
    """)) == [39]

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a=b[c:d]
        ): pass
    """)) == [29]


def test_no_add_exists():
    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            param=value,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            *args,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            param=value,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *,
            param=value,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            *,
            param=value,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *args,
            param=value,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *args,
            param=value,
            **kwargs,
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
            a,
            *args,
            param=value,
            **kwargs,  # comment
        ): pass
    """)) == []


def test_no_add_ignore():
    assert find_missing_trailing_commas(dedent("""
        async def test(): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(
        ): pass
    """)) == []

    assert find_missing_trailing_commas(dedent("""
        async def test(

        ): pass
    """)) == []
