import graph_tool.all as gt
import numpy as np
import matplotlib.pyplot as plt
import polars as pl

import csv
from pathlib import Path
from collections import defaultdict

g = gt.load_graph("lab/4267/projected_graph.gt.gz")

state = gt.minimize_nested_blockmodel_dl(g, state_args=dict(deg_corr=True))

state.draw(output="teste_hier.svg")
