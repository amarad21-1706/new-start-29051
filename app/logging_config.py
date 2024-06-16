import logging
from flask import Flask, request


class ExcludeRequestsFilter(logging.Filter):
    def filter(self, record):
        return not (record.args and len(record.args) > 0 and record.args[0] in ["GET", "POST", "PUT", "DELETE"])

