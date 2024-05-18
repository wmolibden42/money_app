from aiogram import types, executor, Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import basa
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

TOKEN_API = os.environ.get("BOT_TOKEN")
#PROXY_URL = "http://proxy.server:3128"
bot = Bot(TOKEN_API)
#bot = Bot(proxy=PROXY_URL, token=TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class TableStatesGroup(StatesGroup):
    moneyintup = State()
    moneynameup = State()
    money_up = State()
    moneyintdw = State()
    moneynamedw = State()
    money_down = State()


async def on_startup(_):
    basa.db_connect()
    print('Connect in BD true')


button_up = KeyboardButton('Добавить доходы')
button_down = KeyboardButton('Добавить расходы')
button_history = KeyboardButton('Статистика')

start_kb = ReplyKeyboardMarkup()
start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_up, button_down).add(
    button_history)

bt_day = KeyboardButton('Статистика за сегодня')
bt_month = KeyboardButton('Статистика за месяц')
bt_year = KeyboardButton('Статистика за все время')

history_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(bt_day, bt_month).add(bt_year)

bt_food = KeyboardButton('Продукты')
bt_taxi = KeyboardButton('Транспорт')
bt_def = KeyboardButton('Обязательные платежи')
bt_fun = KeyboardButton('Развлечение')
bt_gift = KeyboardButton('Подарки')
bt_oft = KeyboardButton('Другое')

class_kb = ReplyKeyboardMarkup
class_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(bt_food, bt_def, bt_taxi).add(bt_gift,
                                                                                                               bt_fun,
                                                                                                               bt_oft)

bt_zp = KeyboardButton('Зарплата')
bt_pod = KeyboardButton('Подработка/премия')
bt_dr = KeyboardButton('Другое')

plus_kb = ReplyKeyboardMarkup
plus_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(bt_zp, bt_pod).add(bt_dr)

bt_del = KeyboardButton('DeleteAll')
kb_del = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(bt_del)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("""
    Добро пожаловать в полезный, а главное -- бесплатный помощник!
    Я еще не многому научен, но я развиваюсь! Спасибо тебе за выбор именно меня! """, reply_markup=start_kb)


@dp.message_handler(text='Статистика')
async def stat_analyz(message: types.Message):
    await message.answer(basa.stat(user_id=message.from_user.id), reply_markup=kb_del)

@dp.message_handler(text='DeleteAll')
async def del_stat(message: types.Message):
    await message.answer(basa.delete_records(user_id=message.from_user.id), "Ваша статистика успешно удалена! Вы можете начать вести бюджет заново!")


@dp.message_handler(text='Добавить доходы')
async def add_mup(message: types.Message):
    await message.answer('Какую сумму ты хочешь добавить к доходам?')
    await TableStatesGroup.moneyintup.set()


@dp.message_handler(state=TableStatesGroup.moneyintup)
async def state_moneyup(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['money_up'] = message.text
        try:
            data['money_up'] = int(message.text)
            await message.reply('Откуда она у тебя появилась?', reply_markup=plus_kb)
            await TableStatesGroup.next()
        except ValueError:
            await message.answer("Напиши целое число доходов...")


@dp.message_handler(state=TableStatesGroup.moneynameup)
async def state_moneynameup(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['money_name_up'] = message.text
        data['user_id'] = message.from_user.id
        data['now'] = datetime.now(timezone.utc)
        data['date'] = data['now'].date()

    basa.create_new_mup(user_id=data['user_id'], date=data['date'], money_up=data['money_up'], money_name_up=data['money_name_up'])
    await message.reply('Спасибо! Я запомнил! Не забывай фиксировать расходы и доходы!', reply_markup=start_kb)
    await state.finish()


@dp.message_handler(text='Добавить расходы')
async def add_posice_down(message: types.Message):
    await message.answer('Какую сумму ты потратила?')
    await TableStatesGroup.moneyintdw.set()


@dp.message_handler(state=TableStatesGroup.moneyintdw)
async def state_moneydw(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['money_down'] = message.text
        try:
            data['money_down'] = int(message.text)
            await message.reply('На что ты ее потратил(а)?', reply_markup=class_kb)
            await TableStatesGroup.next()
        except ValueError:
            await message.answer("Напиши целое число расходов...")




@dp.message_handler(state=TableStatesGroup.moneynamedw)
async def state_moneynamedw(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['money_name_dw'] = message.text
        data['user'] = message.from_user.id
        data['now'] = datetime.now(timezone.utc)
        data['date'] = data['now'].date()

    basa.create_new_mdw(user=data['user'], date=data['date'], money_down=data['money_down'],
                        money_name_dw=data['money_name_dw'])
    await message.reply('Спасибо! Я запомнил! Не забывай фиксировать расходы и доходы!', reply_markup=start_kb)
    await state.finish()




if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)