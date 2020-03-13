import crayfish
from configuration import Configuration

def run_basic_test ():
    config = Configuration(
        False,
        True,
        ['test'],
        [],
        'test/complete_test.csv',
        'test/test_row_output.csv',
        'test/test_age_output.csv'
    )
    crayfish.run(config)

run_basic_test()