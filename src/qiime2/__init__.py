# ----------------------------------------------------------------------------
# Copyright (c) 2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import importlib
import importlib.abc
import importlib.util

import rachis


# The `.` prevents the hook from running on the root, which doesn't
# help. The root is handled by the __dunders__ below
QIIME2_PREFIX = "qiime2."
RACHIS_PREFIX = "rachis."


def __getattr__(name):
    self = sys.modules[__name__].__dict__
    try:
        # mostly for __version__, but could handle other things
        return getattr(self, name)
    except AttributeError:
        try:
            return getattr(rachis, name)
        except AttributeError:
            # this is just to raise the right error
            getattr(self, name)


def __dir__():
    return dir(rachis)


# The goal is to produce `sys.modules[]` such that
# sys.modules['qiime2.<foo>'] is sys.modules['rachis.<foo>']
# i.e. they must be the same object and only constructed once.
# To do this, we need to intercept imports to both `rachis` and
# `qiime2`. We also need to dodge the typical module initialization
# and instead return our cached module while retaining the true spec.
class QIIME2AliasLoader(importlib.abc.Loader):
    def __init__(self, fullname, target_name):
        # fullname and target_name are _either_ qiime2 or rachis
        # the target_name is the entity that is either already in
        # sys.modules or ought to be.
        self.fullname = fullname
        self.target_name = target_name

    def create_module(self, spec):
        # this is an unusual override, most loaders return None, but
        # by doing this, we can instantiate the module object ourselves
        # it is conceptually similiar to Class.__new__
        target = importlib.import_module(self.target_name)
        sys.modules[self.target_name] = target
        # store the spec for after the import bootstrapping system has
        # rewritten the dunders like __name__. __spec__ is interesting
        # in that an existing value is not respected
        self.spec = target.__spec__
        return target

    def exec_module(self, module):
        # We should only exist if the true module is already cached

        # attach the original spec back onto the module, effectively
        # erasing the trace of all of this machinery.
        module.__spec__ = self.spec
        # shortly after this point we should have two entries in
        # sys.modules:
        # `sys.modules[self.fullname] = module` created by the import
        # `sys.modules[self.target_name] = module` created by us
        # and the final spec of the module should still be the rachis
        # original, which lets package data resolve correctly.


class QIIME2AliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # Check if we have a cache of qiime2.foo

        # If we don't then we would see something like:
        # {'qiime2.foo', 'rachis.foo', 'qiime2.foo.bar'}
        # when we want:
        # {'qiime2.foo', 'rachis.foo', qiime2.foo.bar', 'rachis.foo.bar'}
        if fullname.startswith(RACHIS_PREFIX):
            q2_cached_module = QIIME2_PREFIX + fullname[len(RACHIS_PREFIX):]
            # if we don't have it already under qiime2, then let a standard
            # import hook resolve it, we might see it again someday from a
            # qiime2 import
            if q2_cached_module not in sys.modules:
                return None
            # what our loader will resolve the new module to
            target_name = q2_cached_module

        elif not fullname.startswith(QIIME2_PREFIX):
            # not rachis or qiime2
            return None
        else:

            # our target is the rachis module that either does or will exist
            target_name = RACHIS_PREFIX + fullname[len(QIIME2_PREFIX):]

        try:
            # prove the target exists, this can be either qiime2 or rachis,
            # but sys.modules will either already have qiime2 in it, so the
            # spec becomes whatever the loader said, or it will be rachis in
            # which case either pre-imported or not does not matter
            target_spec = importlib.util.find_spec(target_name)
        except ModuleNotFoundError:
            return None

        if target_spec is None:
            # more or less results in a ModuleNotFound
            return None

        spec = importlib.util.spec_from_loader(
            fullname,
            QIIME2AliasLoader(fullname, target_name),
            origin=target_spec.origin,
            is_package=True,
        )
        # this spec will then be used by the import machinery to load the loader
        return spec


sys.meta_path.insert(0, QIIME2AliasFinder())
