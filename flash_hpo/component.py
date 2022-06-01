from typing import Dict, Any, List, Optional

from lightning import LightningFlow, LightningWork


# GridSearch, RandomSearchStrategy, OptunaSearch
# Maybe we don't need works...
# LightningFlow that's given a work class
# class RandomSearch(LightningWork):
#     def preprocess_hpo_dict(...):
#
#     def 

class FlashHPO(LightningFlow):
    """
    The HPO Component is used to suggest a list of configurations (hyper-parameters) to run with some config
    from the user for any task.

    This component doesn't come with a default UI. Please consider adding a UI yourself based on your task and needs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.generated_runs: Optional[List[Dict[str, Any]]] = None
        self.hpo_dict = {}
        self.num_runs = 0
        self.results = []

    # Having strategy as a class allows the users to define their own strategy class
    def run(self, hpo_dict: dict, num_runs: int=1, strategy_cls=None, work_cls: LightningWork=None, *args, **kwargs):
        if self.generated_runs is not None:
            # clean-up
            self.generated_runs = None

        self.hpo_dict = hpo_dict
        self.num_runs = num_runs

        assert hasattr(strategy_cls, "preprocess"), "`preprocess` function not implemented in the given strategy class."
        assert hasattr(strategy_cls, "generate_runs"), "`generate_runs` function not implemented in the given strategy class."

        # TODO: Figure out a way to let users pass extra args to the strategy class as well
        # Just like the work class (work_cls) below

        # Thought: maybe we should receive an object, and not the class...? Let them instantiate it with the args they want to store?
        strategy = strategy_cls()
        strategy.run(num_runs=num_runs, hpo_config_dict=hpo_dict)

        # Now pass the generated_runs to the given work_cls
        assert strategy.runs is not None, "The strategy class did not generate any runs! Probably something went wrong..."
        self.results.append(strategy.runs)
        work_cls().run(strategy.runs, *args, **kwargs)
        # hpo_dict = strategy_cls.preprocess(hpo_dict)
        # self.generated_runs = strategy_cls.generate_runs(num_runs, hpo_dict)
