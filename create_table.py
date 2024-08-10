import asyncio
import logging
import re
import aiosqlite as sqlite
from var import DB_NAME, TABLE_QA, TABLE_UA, quiz_data


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

class DBTableManager:
    def __init__(self,db_name):
        self.db_name = db_name

    async def create_table(self,table_name: str,fields: str):
        self.check_sql_commands(f"{table_name} {fields}")

        async with sqlite.connect(self.db_name) as db:
            await db.execute(
                f"""CREATE TABLE IF NOT EXISTS {table_name} ({fields})"""
            )
            await db.commit()
        return 0

    async def update_table(self,table_name:str, fields: str, values: tuple):
        t_values = ", ".join(f"'{name}'" for name in values)
        self.check_sql_commands(f"{table_name} {fields} {t_values}")

        async with sqlite.connect(self.db_name) as db:
            await db.execute(
                f"""INSERT INTO {table_name}({fields}) VALUES ({t_values})"""
            )
            await db.commit()

    async def drop_table(self, table_name: str):
        self.check_sql_commands(f"{table_name}")

        async with sqlite.connect(self.db_name) as db:
            await db.execute(f"""DROP TABLE IF EXISTS {table_name}""")

    async def check_table(self,table_name: tuple):
        table_names = ', '.join(f"'{name}'" for name in table_name)
        self.check_sql_commands(f"{table_name}")

        async with sqlite.connect(self.db_name) as db:
            async with db.execute(
                f"""SELECT name FROM sqlite_master WHERE name IN  ({table_names})"""
            ) as cursor:
                table = await cursor.fetchall()
                if table:
                    logger.info(f"Table '{table}' exists.")
                else:
                    raise Exception("function name 'check_table' ERROR, table not found")

    async def just_query(self, **kwargs):
        names_columns, table_name = kwargs.values()
        names_columns = "*" if names_columns == ("*",) else ", ".join(f"'{name}'" for name in names_columns)
        self.check_sql_commands(f"{table_name} {names_columns}")

        async with sqlite.connect(self.db_name) as db:
            async with db.execute(
                f"""SELECT {names_columns} FROM {table_name}"""
            ) as cursor:
                results = await cursor.fetchall()
                if results is not None:
                    return results
                else:
                    return 0


    async def get_data(self, **kwargs):
        names_columns, table_name, w_name_col, w_col_value = kwargs.values()
        names_columns = "*" if names_columns == ("*",) else ", ".join(f"{name}" for name in names_columns)
        self.check_sql_commands(f"{table_name} {names_columns} {w_name_col} {w_col_value}")

        async with sqlite.connect(self.db_name) as db:
            async with db.execute(
                f"""SELECT {names_columns} FROM {table_name} WHERE {w_name_col}={w_col_value}"""
            ) as cursor:
                results = await cursor.fetchone()
                if results is not None:
                    return results
                else:
                    return 0
                
    async def get_data_all(self, **kwargs):
        names_columns, table_name, w_name_col, w_col_value = kwargs.values()
        names_columns = "*" if names_columns == ("*",) else ", ".join(f"{name}" for name in names_columns)
        self.check_sql_commands(f"{table_name} {names_columns} {w_name_col} {w_col_value}")

        async with sqlite.connect(self.db_name) as db:
            print( f"""SELECT {names_columns} FROM {table_name} WHERE {w_name_col}={w_col_value}""")
            async with db.execute(
                f"""SELECT {names_columns} FROM {table_name} WHERE {w_name_col}={w_col_value}"""
            ) as cursor:
                results = await cursor.fetchall()
                if results is not None:
                    return results
                else:
                    return 0

    async def get_max_val(self, **kwargs):
        names_columns, table_name, w_name_col, w_col_value = kwargs.values()
        self.check_sql_commands(f"{table_name} {names_columns} {w_name_col} {w_col_value}")

        async with sqlite.connect(self.db_name) as db:
            async with db.execute(
                f"""SELECT MAX({names_columns}) FROM {table_name} WHERE {w_name_col}={w_col_value}"""
            ) as cursor:
                results = await cursor.fetchone()
                if results is not None:
                    return results
                else:
                    return 0


    def check_sql_commands(self, input_string: str):
        sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 
            'CREATE', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE'
        ]
        
        input_string_upper = input_string.upper()
        
        pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in sql_keywords) + r')\b'
        
        if re.search(pattern, input_string_upper):
            raise ValueError("SQL command detected")

    async def reset_table(self,table_name: str, field: str):
        await self.drop_table(table_name)
        await self.create_table(table_name, field)
        logger.info(f"reset_table {table_name}")

async def add_questions(**kwargs):
    try:
        obj_sqlite, t_name, t_fields, t_values = kwargs.values()
        for obj_quiz in t_values:
            question, options, correct_option = obj_quiz.values()
            options = ",".join(options)
            values = (question, options, correct_option)
            await obj_sqlite.update_table( t_name, t_fields, values)
        logger.info("add_questions completed successfully")
    except ValueError as e:
        raise Exception(f"add_questions ERROR. {e}")




async def init_table():
    qa_field = "num_q INTEGER PRIMARY KEY, question TEXT, answer TEXT, r_answer INTEGER"
    ua_field = "user_id INTEGER, num_q INTEGER, answer TEXT, time INTEGER"

    dbtm = DBTableManager(DB_NAME)
    await dbtm.reset_table(TABLE_QA,qa_field)
    await dbtm.reset_table(TABLE_UA,ua_field)
    await dbtm.check_table((TABLE_QA, TABLE_UA))

    await add_questions(
        obj_sqlite=dbtm,
        t_name=TABLE_QA,
        t_fields="question,answer,r_answer",
        t_values=quiz_data,
    )

async def main():
    await init_table()

# asyncio.run(main())
