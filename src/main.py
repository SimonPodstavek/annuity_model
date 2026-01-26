from pandas import DataFrame
from config.schemas import config
from data_io.excel import read_xlsx



def main() -> None:

    baseline_mortality_df = read_xlsx(config.dataset.baseline_mortality_path)
    baseline_mortality_df





if __name__ == "__main__":
    main()