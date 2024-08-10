import asyncio
import logging
import time
import nest_asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types, F
from var import DB_NAME, TABLE_QA, TABLE_UA, API_TOKEN
from create_table import DBTableManager

nest_asyncio.apply()
logger = logging.getLogger()
logging.basicConfig(level=logging.WARNING)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dbtm = DBTableManager(DB_NAME)

async def get_user_data(user_id):
    result = await dbtm.get_data(
        names_columns=("*",),
        table_name=TABLE_UA,
        w_name_col="user_id",
        w_col_value=user_id,
    )
    return result

async def get_num_q(num_question):
    result = await dbtm.get_data(
        names_columns=("*",),
        table_name=TABLE_QA,
        w_name_col="num_q",
        w_col_value=num_question,
    )
    return result

async def get_max_num_q(user_id):
    result = await dbtm.get_max_val(
            names_columns="num_q",
            table_name=TABLE_UA,
            w_name_col="user_id",
            w_col_value=user_id,
        )
    return result

def count_answers(answers):
    correct_count = 0
    incorrect_count = 0

    for answer in answers:
        if answer[0] == 'right_answer':
            correct_count += 1
        elif answer[0] == 'wrong_answer':
            incorrect_count += 1

    return correct_count, incorrect_count

async def answer_questions(message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Ответить на вопросы"))
    await message.answer(
        "Жми на кнопку **Ответить на вопросы**",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    is_user = await get_user_data(user_id)

    if is_user:
        user_id, num_q, answ, time = is_user
        num_q = await get_max_num_q(user_id)
        count_q = await dbtm.just_query(        
            names_columns=("num_q",),
            table_name=TABLE_QA
        )
        num_q = int(num_q[0])
        num_q +=1
        if num_q > len(count_q):
            await message.answer("Вы прошли опрос. Спасибо", reply_markup=None)
            return 0
        else:
            await answer_questions(message)
    else:
        await answer_questions(message)

@dp.message(F.text == "Ответить на вопросы")
async def start_quiz(message: types.Message):
    await message.answer("Запуск опроса", reply_markup=types.ReplyKeyboardRemove())
    await quiz(message)


async def quiz(message):
    user_id = message.from_user.id
    is_user = await get_user_data(user_id)

    if is_user:
        user_id, num_q, answ, time = is_user
        max_val_tpl = await get_max_num_q(user_id)
        max_val = max_val_tpl[0]
        print(max_val, type(max_val))
        max_val += 1
        question_data = await get_num_q(max_val)
    else:
        question_data = await get_num_q(1)
    await data_output(message, question_data)

async def data_output(message,question_data):
    index, q, a, ra = question_data
    a = a.split(',')
    kb = generate_options_keyboard(a, ra, index)
    await message.answer(
        f"{q}", reply_markup=kb
    )


def generate_options_keyboard(answer_options, right_answer, q_index):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data=(
                    f"""{q_index}:{
                        "right_answer" if option == answer_options[right_answer]
                        else "wrong_answer"}"""
                ),
            )
        )

    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(lambda c: c.data)
async def handle_callback(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    num_q, answer = (callback.data).split(":")
    num_q = int(num_q)
    q_time = int(time.time())
    await dbtm.update_table(
        table_name=TABLE_UA,
        fields="user_id, num_q, answer, time",
        values=(user_id, num_q, answer, q_time),
    )

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    num_q +=1
    count_q = await dbtm.just_query(        
        names_columns=("num_q",),
        table_name=TABLE_QA
    )

    if num_q > len(count_q):
        user_answer = await dbtm.get_data_all(        
            names_columns = ("answer",),
            table_name = TABLE_UA,
            w_name_col = "user_id", 
            w_col_value = user_id
        )
        c_answer = count_answers(user_answer)
        result_str = f"Опрос завершен, спасибо.\nПравильных ответов: {c_answer[0]}\nОшибок: {c_answer[1]}"
        await callback.message.answer(
            text=result_str, reply_markup=None
        )
        return 0

    question_data = await get_num_q(num_q)

    await data_output(callback.message, question_data)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
