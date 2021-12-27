from datetime import datetime
from setup import load_data
import plot_data_functions as hairyPlotter


if __name__ == "__main__":
    # setup
    token="LRC"
    start_date = datetime(2021, 12, 20, 12, 00, 00)
    end_date = datetime(2021, 12, 27, 13, 00, 00)

    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
    ]

    token_data, project_commits = load_data(
        token,
        project_repos,
        start_date,
        end_date,
        pickle_data_interval = 'week',
        read_from_pickle = False,
        write_to_pickle = False
    )

    # it's levioSA
    hairyPlotter.show_commmit_plot(token_data, project_commits)