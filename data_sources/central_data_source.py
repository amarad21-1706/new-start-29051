from abc import ABC, abstractmethod

from data_sources.central_data import CentralData

class DataSource(ABC):
    @abstractmethod
    def query(self, page, per_page):
        pass


class CentralDataDataSource(DataSource):
    def __init__(self):
        # Connect to the database
        from app import db
        self.db = db

    def query(self, page, per_page):
        # Retrieve paginated data from the CentralData model
        pagination = CentralData.query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items  # Return only the items, not the entire pagination object
