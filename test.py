import pytest
from dbclasses import *


# Test of the table_difference() method.

@pytest.fixture
def table_setup_table_difference():
    table1 = Table("TestTable1")
    table1.add_column("col1", Type.integer)
    table1.add_column("col2", Type.string)

    table2 = Table("TestTable2")
    table2.add_column("col1", Type.integer)
    table2.add_column("col2", Type.string)
    return table1, table2


def test_table_difference_identical_tables(table_setup_table_difference):
    table1, table2 = table_setup_table_difference

    table1.add_row({"col1": "1", "col2": "test1"})
    table1.add_row({"col1": "2", "col2": "test2"})
    table2.add_row({"col1": "1", "col2": "test1"})
    table2.add_row({"col1": "2", "col2": "test2"})

    difference = table1.table_difference(table2)
    assert len(difference) == 0, "The tables are identical, but the difference is not empty."


def test_table_difference_partial_match(table_setup_table_difference):
    table1, table2 = table_setup_table_difference

    table1.add_row({"col1": "1", "col2": "test1"})
    table1.add_row({"col1": "2", "col2": "test2"})
    table1.add_row({"col1": "3", "col2": "test3"})

    table2.add_row({"col1": "1", "col2": "test1"})
    table2.add_row({"col1": "3", "col2": "test3"})

    difference = table1.table_difference(table2)
    assert len(difference) == 1
    assert difference[0].values["col1"] == 2
    assert difference[0].values["col2"] == "test2"


def test_table_difference_no_match(table_setup_table_difference):
    table1, table2 = table_setup_table_difference

    table1.add_row({"col1": "1", "col2": "test1"})
    table1.add_row({"col1": "2", "col2": "test2"})

    table2.add_row({"col1": "3", "col2": "test3"})
    table2.add_row({"col1": "4", "col2": "test4"})

    difference = table1.table_difference(table2)
    assert len(difference) == 2
    assert any(row.values["col1"] == 1 for row in difference)
    assert any(row.values["col1"] == 2 for row in difference)


def test_table_difference_different_columns():
    table1 = Table("TestTable1")
    table1.add_column("col1", Type.integer)
    table1.add_column("col2", Type.string)

    table2 = Table("TestTable2")
    table2.add_column("col1", Type.integer)
    table2.add_column("col3", Type.real)

    with pytest.raises(ValueError, match="Таблиці мають різні колонки. Оберіть інші таблиці."):
        table1.table_difference(table2)


# Test of the add_row() method.

@pytest.fixture
def setup_table_with_columns():
    table = Table("TestTable")
    table.add_column("int_col", Type.integer)
    table.add_column("real_col", Type.real)
    table.add_column("char_col", Type.char)
    table.add_column("string_col", Type.string)
    table.add_column("time_col", Type.time)
    table.add_column("timeInvl_col", Type.timeInvl)
    return table


def test_add_row_all_correct(setup_table_with_columns):
    table = setup_table_with_columns

    result = table.add_row({
        "int_col": "5",
        "real_col": "5.5",
        "char_col": "c",
        "string_col": "test",
        "time_col": "12:30:45",
        "timeInvl_col": "10:00:00-12:00:00"
    })
    assert result == True, "The row should be added successfully"
    assert len(table.rows) == 1, "One row should be added"


def test_add_row_most_incorrect(setup_table_with_columns):
    table = setup_table_with_columns

    with pytest.raises(ValidError) as excinfo:
        table.add_row({
            "int_col": "invalid",
            "real_col": 2.6,
            "char_col": "too_long",
            "string_col": 123,
            "time_col": "25:61:61",
            "timeInvl_col": "12:00:00-10:00:00"
        })

    assert "int_col" in str(excinfo.value)
    assert "char_col" in str(excinfo.value)
    assert "time_col" in str(excinfo.value)
    assert "timeInvl_col" in str(excinfo.value)
    assert len(table.rows) == 0, "The row should not be added"


def test_add_row_some_invalid_some_empty(setup_table_with_columns):
    table = setup_table_with_columns

    with pytest.raises(ValidError) as excinfo:
        table.add_row({
            "int_col": "invalid",
            "real_col": "",
            "char_col": None,
            "string_col": "valid_string",
            "time_col": "12:00:00",
            "timeInvl_col": None
        })

    assert "int_col" in str(excinfo.value)
    assert "char_col" not in str(excinfo.value)
    assert "time_col" not in str(excinfo.value)
    assert len(table.rows) == 0, "The row should not be added"


def test_add_row_all_empty(setup_table_with_columns):
    table = setup_table_with_columns

    with pytest.raises(ValueError, match="Усі поля порожні"):
        table.add_row({
            "int_col": None,
            "real_col": None,
            "char_col": None,
            "string_col": None,
            "time_col": None,
            "timeInvl_col": None
        })

    assert len(table.rows) == 0, "The row should not be added"


def test_add_row_some_correct_some_empty(setup_table_with_columns):
    table = setup_table_with_columns

    result = table.add_row({
        "int_col": "10",
        "real_col": None,
        "char_col": "a",
        "string_col": "",
        "time_col": "10:30:00",
        "timeInvl_col": None
    })

    assert result == True, "The row should be added successfully"
    assert len(table.rows) == 1, "One row should be added"


# Test of the add_column() method.

@pytest.fixture
def table_setup_add_row():
    table = Table("TestTable")
    table.add_column("col1", Type.string)
    return table


def test_add_empty_column_name(table_setup_add_row):
    table = table_setup_add_row

    with pytest.raises(ValueError, match="Колонка повинна мати назву. Будь ласка, спробуйте ще раз."):
        table.add_column("", Type.integer)

def test_add_existing_column_name(table_setup_add_row):
    table = table_setup_add_row

    with pytest.raises(ValueError, match="Колонка з такою назвою вже існує."):
        table.add_column("col1", Type.integer)


def test_add_new_column_name(table_setup_add_row):
    table = table_setup_add_row
    result = table.add_column("col2", Type.integer)
    assert result == True, "The column should be successfully added"
    assert "col2" in table.columns, "Column col2 must be added"
    assert table.columns["col2"] == Type.integer, "Column type col2 must be integer"
