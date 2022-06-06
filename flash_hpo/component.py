from lightning import LightningFlow


class FlashHPO(LightningFlow):
    """
    The HPO Component is used to suggest a list of configurations (hyper-parameters) to run with some config
    from the user for any task.

    This component doesn't come with a default UI. Please consider adding a UI yourself based on your task and needs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.hpo_dict = {}
        self.num_runs = 0
        self.results = None

    # Having strategy as a class allows the users to define their own strategy class
    def run(self, hpo_dict: dict, num_runs: int=1, strategy=None, work=None, work_kwargs={},
            parallelize=True, *args, **kwargs):
        if self.results is None:
            self.hpo_dict = hpo_dict
            self.num_runs = num_runs

            # Thought: maybe we should receive an object, and not the class...?
            # Let them instantiate it with the args they want to store?
            # Yep^^ done! :)
            if parallelize:
                for run_id in range(num_runs):
                    strategy.run(run_id=run_id, hpo_config_dict=hpo_dict, *args, **kwargs)
            else:
                strategy.run(num_runs=num_runs, hpo_config_dict=hpo_dict, *args, **kwargs)

            # Now pass the runs to the given work_cls
            assert len(strategy.runs) > 0, "The strategy class did not generate any runs! Probably something went wrong..."
            self.results = strategy.runs
            if len(work_kwargs) != 0:
                work.run(self.results, work_kwargs)
            else:
                work.run(self.results)
