from datetime import datetime
from setup import load_data
from HairyPlotter import HairyPlotter


if __name__ == "__main__":
    # setup
    read_from_pickle = False
    token="LRC"
    start_date = datetime(2021, 12, 1, 12, 00, 00)
    end_date = datetime(2021, 12, 2, 12, 00, 00)

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
        pickle_data_interval = 'day',
        read_from_pickle = read_from_pickle,
        write_to_pickle = not read_from_pickle
    )

    # it's levioSA
    hp = HairyPlotter()
    hp.show_commmit_plot(token_data, project_commits)