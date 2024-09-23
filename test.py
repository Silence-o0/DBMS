import pytest
from uuid import uuid4
from dbclasses import *


@pytest.fixture
def table_setup():
    table1 = Table("Table1")
    table1.add_column("col1", Type.integer)
    table1.add_column("col2", Type.string)

    table2 = Table("Table2")
    table2.add_column("col1", Type.integer)
    table2.add_column("col2", Type.string)
    return table1, table2


def test_table_difference_identical_tables(table_setup):
    table1, table2 = table_setup

    table1.add_row({"col1": "1", "col2": "test1"})
    table1.add_row({"col1": "2", "col2": "test2"})
    table2.add_row({"col1": "1", "col2": "test1"})
    table2.add_row({"col1": "2", "col2": "test2"})

    difference = table1.table_difference(table2)
    assert len(difference) == 0, "Таблиці ідентичні, але різниця не порожня."


def test_table_difference_partial_match(table_setup):
    table1, table2 = table_setup

    table1.add_row({"col1": "1", "col2": "test1"})
    table1.add_row({"col1": "2", "col2": "test2"})
    table1.add_row({"col1": "3", "col2": "test3"})

    table2.add_row({"col1": "1", "col2": "test1"})
    table2.add_row({"col1": "3", "col2": "test3"})

    difference = table1.table_difference(table2)
    assert len(difference) == 1
    assert difference[0].values["col1"] == 2
    assert difference[0].values["col2"] == "test2"


def test_table_difference_no_match(table_setup):
    table1, table2 = table_setup

    table1.add_row({"col1": "1", "col2": "test1"})
    table1.add_row({"col1": "2", "col2": "test2"})

    table2.add_row({"col1": "3", "col2": "test3"})
    table2.add_row({"col1": "4", "col2": "test4"})

    difference = table1.table_difference(table2)
    assert len(difference) == 2
    assert any(row.values["col1"] == 1 for row in difference)
    assert any(row.values["col1"] == 2 for row in difference)


def test_table_difference_different_columns():
    table1 = Table("Table1")
    table1.add_column("col1", Type.integer)
    table1.add_column("col2", Type.string)

    table2 = Table("Table2")
    table2.add_column("col1", Type.integer)
    table2.add_column("col3", Type.real)

    with pytest.raises(ValueError, match="Таблиці мають різні колонки. Оберіть інші таблиці."):
        table1.table_difference(table2)


@pytest.fixture
def table_for_row_tests():
    table = Table("TestTable")
    table.add_column("time_col", Type.time)
    table.add_column("interval_col", Type.timeInvl)
    return table


def test_add_row_with_valid_time(table_for_row_tests):
    table = table_for_row_tests

    result = table.add_row({"time_col": "12:30:45", "interval_col": "10:00:00-12:00:00"})
    assert result == True
    assert len(table.rows) == 1
    assert table.rows[next(iter(table.rows))].values["time_col"] == "12:30:45"


def test_add_row_with_invalid_time(table_for_row_tests):
    table = table_for_row_tests

    with pytest.raises(ValidError):
        table.add_row({"time_col": "25:61:00", "interval_col": "10:00:00-12:00:00"})

    assert len(table.rows) == 0


def test_add_row_with_invalid_time_interval(table_for_row_tests):
    table = table_for_row_tests
    with pytest.raises(ValidError):
        table.add_row({"time_col": "12:30:45", "interval_col": "12:00:00-10:00:00"})
    assert len(table.rows) == 0


def test_add_row_with_all_none(table_for_row_tests):
    table = table_for_row_tests
    with pytest.raises(ValueError, match="Усі поля порожні. Введіть, будь ласка, дані."):
        table.add_row({"time_col": None, "interval_col": None})
    assert len(table.rows) == 0
