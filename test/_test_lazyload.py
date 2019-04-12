import numpy
import scipy
import pandas
import sys


def test_lazyload():
    preloaded_modules = set([m.split('.')[0] for m in sys.modules.keys()])
    assert 'scprep' not in preloaded_modules
    import scprep
    postloaded_modules = set([m.split('.')[0] for m in sys.modules.keys()])
    scprep_loaded = postloaded_modules.difference(preloaded_modules)
    for module in scprep._lazyload._importspec.keys():
        assert module not in scprep_loaded, module
