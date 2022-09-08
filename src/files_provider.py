import glob
import logging
from pathlib import Path


class FilesProvider:
    """
    Provide paths to data files.
    Help to search among files with raw data
    """
    __DESTINATION_DIR = "dest"
    __RAW_HTML_MESSAGES_MASK = "messages*.html"

    def __init__(self, raw_data_dir: Path, logger: logging.Logger) -> None:
        self.logger = logger
        self.__raw_data_dir = raw_data_dir
        self.__check_raw_data_dir()

    def __check_raw_data_dir(self) -> None:
        if not self.__raw_data_dir.is_dir():
            raise ValueError(f'Path [{self.__raw_data_dir}] does not exist or it is not a dir!')

    def get_dest_file_path(self, additional_info: list[str]) -> Path:
        file_name = f'{self.__DESTINATION_DIR}/messages_' + '_'.join(additional_info)
        truncated_file_name = (file_name[:100] + '..') if len(file_name) > 100 else file_name
        
        return Path(truncated_file_name + '.tsv')

    def get_all_raw_file_paths(self) -> list[Path]:
        file_paths = [Path(file_path) for file_path in
                      glob.glob(str(self.__raw_data_dir / self.__RAW_HTML_MESSAGES_MASK))]

        files_count = len(file_paths)
        if files_count == 0:
            self.logger.error(f'Path [{self.__raw_data_dir}] does not contain any files with messages!')

        self.logger.debug(f'There are {files_count} files for parsing in {self.__raw_data_dir}.')
        return file_paths
