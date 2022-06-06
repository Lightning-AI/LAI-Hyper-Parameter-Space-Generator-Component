from typing import List, Any

from lightning import LightningFlow, LightningApp, LightningWork
from lightning.frontend import StreamlitFrontend
from lightning.utilities.state import AppState


from flash_hpo import FlashHPO, RandomSearchStrategy, GridSearchStrategy


class DoSomethingExtra(LightningWork):
    def __init__(self):
        super().__init__(run_once=True)
        self.hpo_list = []

    def run(self, hpo_list: List[Any], *wargs, **kwargs):
        self.hpo_list.extend(hpo_list)
        with open("work_output.txt", "a") as _file:
            _file.write(str(len(self.hpo_list)))


def _render_fn(state: AppState):
    import streamlit as st
    import pandas as pd

    st.title("Hyper Parameters from the given runs")

    if state.data is None:
        st.write("We are working on receiving the data... hold on!")
        return

    st.write(pd.DataFrame(state.data))


class Visualizer(LightningFlow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def run(self, data):
        self.data = data

    def configure_layout(self):
        return StreamlitFrontend(render_fn=_render_fn)


def train_func(config):
    """
    A sample training function to be used for GridSearchStrategy
    """
    from ray import tune
    import torch.optim as optim

    from ray.tune.examples.mnist_pytorch import get_data_loaders, ConvNet, train, test

    train_loader, test_loader = get_data_loaders()
    model = ConvNet()
    optimizer = optim.SGD(model.parameters(), lr=config["learning_rate"])
    for _ in range(10):
        train(model, optimizer, train_loader)
        acc = test(model, test_loader)
        tune.report(mean_accuracy=acc)


class HPOComponent(LightningFlow): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hpo = FlashHPO()
        self.work_random_search = DoSomethingExtra()
        self.work_grid_search = DoSomethingExtra()
        self.visualize = Visualizer()
        self.results = None

    def run(self):
        # Currently, base functions of each strategy only support backbone and learning_rate
        # If you want, you can write your own preprocess functions, or just pass a preprocessed dict
        # as shown below in the comments, and pass should_preprocess=False in the class instantiation.
        # hpo_config = {
        #     "backbone": ["pral1/bert-tiny", "pra1/bert-medium"],
        #     "learning_rate": [0.01, 1.0],
        #     "n_epochs": 10,
        #     "batch_size": [1, 10],
        # }

        hpo_config = {
            "backbone": ["prajjwal1/bert-tiny", "pra1/bert-medium"],
            "learning_rate": [0.000001, 0.1],
        }

        # work_cls allows you to use the hyper-paramaters from the given num_runs
        # basically .run() method is called with the HPOs from the HPO component after this
        # self.hpo.run(hpo_dict=hpo_config, num_runs=5,
        #              work=self.work_random_search, strategy=RandomSearchStrategy(should_preprocess=True))

        # Make sure that the estimator function reports the given metric using: (example)
        # tune.report(mean_accuracy=acc)
        self.hpo.run(hpo_dict=hpo_config, num_runs=5,
                     strategy=GridSearchStrategy(should_preprocess=True), work=self.work_grid_search,
                     estimator=train_func, mode="max", metric="mean_accuracy",
                     parallelize=False)

        if self.work_grid_search.has_succeeded:
            self.visualize.run(self.hpo.results)

    def configure_layout(self):
        return {"name": "HPO Output", "content": self.visualize}


# To launch the HPO Component
app = LightningApp(HPOComponent(), debug=True)
