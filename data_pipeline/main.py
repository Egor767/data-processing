from data_pipeline.src.checks import checks
from data_pipeline.src.etl import etl
from data_pipeline.src.init_schema import init_schema

if __name__ == "__main__":
    init_schema()
    etl()
    checks()

