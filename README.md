Бот @unrealquiz_bot
Точка входа index.py
Функции работы с базой в файле create_table.py
Файл var.py набор переменных, все вопросы в базе bot.db
bot.db содержит две таблицы:
   - "вопросы ответы"
   - "ответы пользователя"

index.py
   get_user_data(user_id):
      - запрос строки из TABLE_UA по user_id. Возвращает list

   get_num_q(num_question):
      - запрос строки из TABLE_QA по num_question. Возвращает list

   get_max_num_q(user_id):
      - запрос максимальное значение в колонке num_q из TABLE_UA по user_id. Возвращает list

   count_answers(answers):
      - подсчитывает ответы. Возвращает tuple

   answer_questions
      - Ответить на вопросы, клавиатура и текст

   cmd_start
      - Проверяет состояние опроса, текст кнопка

   start_quiz
      -  запускает опрос

   quiz
      - контроль выполнения викторины для конкретного пользователя
         - если пользователь найден продолжить опрос, если нет, то с начала

   data_output(message,question_data):
      - формирует и отправляет пользователю сообщение с вопросом

   generate_options_keyboard(answer_options, right_answer, q_index)
      - генерация клавиатуры

   handle_callback(callback: types.CallbackQuery):
      - обработчик ответа пользователя
         - обновление базы данных
         - очистка клавиатуры
         - вывод следующего вопроса или завершение опроса

   main():
      -  точка входа для запуска бота



create-table.py
   create_table(self,table_name: str,fields: str):
      - создаёт таблицу в db

   update_table(self,table_name:str, fields: str, values: tuple):
      - обновляет записи в db

   drop_table(self, table_name: str):
      - удаляет табличку

   check_table(self,table_name: tuple):
      - проверяет наличие таблиц в db

   just_query(self, **kwargs):
      - запрос вида SELECT FROM
         names_columns: tuple,
         table_name: str

   get_data(self, **kwargs):
      - получает одну строку
         names_columns: tuple, 
         table_name: str, 
         w_name_col: str, (Где имя колонки) 
         w_col_value: str (Соответствует значению)

   get_data_all(self, **kwargs):
      - получает все значение в колонке/ках
         names_columns: tuple, 
         table_name: str, 
         w_name_col: str, (Где имя колонки) 
         w_col_value: str (Соответствует значению)

   get_max_val(self, **kwargs):
      - получает максимальное значение в колонке
         names_columns: str, 
         table_name: str, 
         w_name_col: str, (Где имя колонки) 
         w_col_value: str (Соответствует значению)

   check_sql_commands(self, input_string: str):
      - проверяет входящую переменную на наличие команд

   reset_table(self,table_name: str, field: str):
      - пересоздаёт таблицу 

   add_questions(**kwargs):
      - Добавляет вопросы в базу данных
      **kwargs
         obj_sqlite, 
         t_name: str, 
         t_fields: str, 
         t_values: dict

   init_table():
      - инициализирует таблицы и обновляет db

   main():
      - точка входа


Как использовать
!!! logger установлен в WARNING
- Настроить переменные в файле var.py
- Запустить скрипт asyncio.run в файле create-table.py, если оставить, таблицы будут обновляться
- Запустить скрипт asyncio.run в файле index.py