# some really basic plotting for now
import glob
from os import path
from nbformat import current as nbf
from datetime import datetime
import base
from periphery_configuration import PeripheryConfiguration, PeripheryOutput


def make_notebook(outPath: str, description: str, results: PeripheryOutput, fname=None):
    nb = nbf.new_notebook()
    imports = """
    import numpy as np
    from datetime import datetime
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    matplotlib inline
    """
    cells = [nbf.new_text_cell('markdown', description), nbf.new_code_cell(imports),
             nbf.new_code_cell("plt.plot(results.anfH)")]

    nb['worksheets'].append(nbf.new_worksheet(cells=cells))
    if fname is None:
        fname = 'model output ' + datetime.now().strftime('%d %b %y %H %M') + ".ipynb"

    with open(path.join(outPath, fname), 'w') as _:
        nbf.write(nb, _, 'ipynb')


def make_plots(basePath: str):
    files = glob.glob(path.join(basePath, '**', '*.npy'), recursive=True)
    print(len(files))
    for file in files:
        print(file)


if __name__ == "__main__":
    make_plots(path.join(base.rootPath, PeripheryConfiguration.DataFolder)) # this will never work.
