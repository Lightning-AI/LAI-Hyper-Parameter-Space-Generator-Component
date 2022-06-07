from typing import Dict, Any

from flash_hpo import SearchStrategy

from sklearn.model_selection import ParameterGrid


class GridSearchStrategy(SearchStrategy):
    def __init__(self, should_preprocess=False, *args, **kwargs):
        super().__init__(should_preprocess=should_preprocess, *args, **kwargs)

    def run(self, hpo_config_dict: Dict[str, Any], run_id=-1):
        if self.should_preprocess:
            hpo_config_dict = self.preprocess(hpo_config_dict)

        self.runs.extend(self.generate_runs(run_id, hpo_config_dict))

    def preprocess(self, hpo_dict):
        """
        We don't need to perform any preprocessing here, assuming correct configuration is passed.

        For what is supported, consult: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterGrid.html
        """
        return hpo_dict

    def generate_runs(self, run_id: int, model_config: dict):
        runs = []
        config_dict = {"id": run_id}
        param_grid = list(ParameterGrid(model_config))
        for ind, val in enumerate(param_grid):
            config_dict[f"Space Index: {ind}"] = val
        runs.append(
            config_dict
        )
        return runs