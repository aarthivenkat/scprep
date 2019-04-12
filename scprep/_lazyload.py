import importlib
import sys

# Key:
# { module : [{submodule1:[subsubmodule1, subsubmodule2]}, submodule2] }
# each module loads submodules on initialization but is only imported
# and loads methods/classes when these are accessed
_importspec = {
    'matplotlib': ['colors', 'pyplot', 'animation', 'cm',
                   'axes', 'lines', 'ticker', 'transforms'],
    'mpl_toolkits': ['mplot3d'],
    'fcsparser': ['api'],
    'rpy2': [{'robjects': ['numpy2ri', 'packages', 'vectors', 'conversion']},
             'rinterface',
             {'rinterface_lib': ['callbacks']}],
    'h5py': [],
    'tables': []
}


class AliasModule(object):

    def __init__(self, name, members=None):
        # easy access to AliasModule members to avoid recursionerror
        super_setattr = super().__setattr__
        if members is None:
            members = []
        super_setattr('__module_name__', name)
        super_setattr('__module_members__', members)
        super_setattr('__loaded__', False)
        # create submodules
        submodules = []
        for member in members:
            if isinstance(member, dict):
                for submodule, submembers in member.items():
                    super_setattr(submodule, AliasModule(
                        "{}.{}".format(name, submodule), submembers))
                    submodules.append(submodule)
            else:
                super_setattr(member, AliasModule(
                    "{}.{}".format(name, member)))
                submodules.append(member)
        super_setattr("__submodules__", submodules)

    @property
    def __loaded_module__(self):
        # easy access to AliasModule members to avoid recursionerror
        super_getattr = super().__getattribute__
        super_setattr = super().__setattr__
        name = super_getattr("__module_name__")
        if not super_getattr("__loaded__"):
            # module hasn't been imported yet
            importlib.import_module(name)
            super_setattr('__loaded__', True)
        # access lazy loaded member from loaded module
        return sys.modules[name]

    def __getattribute__(self, attr):
        # easy access to AliasModule members to avoid recursionerror
        super_getattr = super().__getattribute__
        if attr in super_getattr("__submodules__"):
            # accessing a submodule, return directly
            return super_getattr(attr)
        else:
            # accessing an unknown member
            # access lazy loaded member from loaded module
            return getattr(super_getattr("__loaded_module__"), attr)

    def __setattr__(self, name, value):
        # allows monkey-patching
        # easy access to AliasModule members to avoid recursionerror
        super_getattr = super().__getattribute__
        return setattr(super_getattr("__loaded_module__"), name, value)


# load required aliases into global namespace
# these can be imported as
# from scprep._lazyload import matplotlib
# plt = matplotlib.pyplot
for module, members in _importspec.items():
    globals()[module] = AliasModule(module, members)
