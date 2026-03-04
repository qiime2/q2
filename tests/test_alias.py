def test_import_identities():
    # Testing more than this isn't helpful as modules will be
    # cached and it's not going to be easy to predict future
    # import order.
    # Demonstrating that these instances are identical is fine.
    from qiime2.core.testing.type import IntSequence1 as i1
    from rachis.core.testing.type import IntSequence1 as i2

    assert i1 is i2
