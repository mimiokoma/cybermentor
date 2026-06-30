from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from states.career_test import CareerTest
from data.questions import QUESTIONS

from data.professions import PROFESSIONS

from data.specialties import SPECIALTIES

from utils.storage import save_user, get_user

from data.goals import GOALS

from agent.brain import (
    ask_ai,
    generate_month_plan
)

from data.resources import (
    BLUE_RESOURCES,
    RED_RESOURCES
)

def build_plan(level):

    if level == "👨‍🎓 Школьник":
        return [
            "Изучить Python",
            "Освоить Linux",
            "Изучить компьютерные сети",
            "Попробовать CTF",
            "Собрать портфолио",
            "Подготовиться к поступлению"
        ]

    elif level == "📝 Абитуриент":
        return [
            "Выбрать направление подготовки",
            "Углубить Python",
            "Изучить Linux",
            "Изучить сети",
            "Участвовать в CTF",
            "Сформировать портфолио"
        ]

    else:
        return [
            "Развивать практические навыки",
            "Работать с Linux и Git",
            "Участвовать в CTF",
            "Проходить стажировки",
            "Выбрать специализацию",
            "Подготовиться к позиции Junior"
        ]

# =========================
# Инициализация
# =========================

bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# =========================
# Главное меню
# =========================

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎯 Профориентация")],
        [KeyboardButton(text="🤖 Задать вопрос наставнику")],
        [KeyboardButton(text="🗺️ Моя карьерная траектория")],
        [KeyboardButton(text="📚 Ресурсы для развития")],
        [KeyboardButton(text="👤 Мой профиль")]
    ],
    resize_keyboard=True
)

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)

# =========================
# Клавиатура оценок
# =========================

rating_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="1"),
            KeyboardButton(text="2"),
            KeyboardButton(text="3"),
            KeyboardButton(text="4"),
            KeyboardButton(text="5")
        ]
    ],
    resize_keyboard=True
)
education_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨‍🎓 Школьник")],
        [KeyboardButton(text="📝 Абитуриент")],
        [KeyboardButton(text="💻 Студент")],
        [KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)

plan_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗺️ Показать траекторию")],
        [KeyboardButton(text="🎯 Изменить цель")],
        [KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)

goal_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=goal)]
        for goal in GOALS
    ] + [
        [KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я CyberMentor 👋\n\nЯ — интеллектуальный карьерный наставник, который помогает школьникам, абитуриентам и студентам построить профессиональную траекторию в сфере кибербезопасности и IT.\n\nВместе мы определим подходящее направление, сформируем карьерную траекторию и подберём ресурсы для развития.",
        reply_markup=menu
    )

@dp.message(F.text == "🏠 Главное меню")
async def back_to_menu(
        message: Message,
        state: FSMContext
):

    await state.clear()

    await message.answer(
        "Главное меню",
        reply_markup=menu
    )

@dp.message(F.text == "🎯 Профориентация")
async def start_test(message: Message, state: FSMContext):

    await state.set_state(
        CareerTest.education_level
    )

    await message.answer(
        "Для начала выберите ваш статус:",
        reply_markup=education_keyboard
    )

@dp.message(F.text == "🤖 Задать вопрос наставнику")
async def mentor_start(
        message: Message,
        state: FSMContext
):

    await state.set_state(
        CareerTest.mentor_chat
    )

    await message.answer(
        "🤖 Привет! На связи ИИ-ассистент. Задайте вопрос по обучению, профессиям или карьере.",
        reply_markup=back_keyboard
    )

# =========================
# Обработка ответов теста
# =========================

@dp.message(CareerTest.education_level)
async def choose_level(
        message: Message,
        state: FSMContext
):

    levels = [
        "👨‍🎓 Школьник",
        "📝 Абитуриент",
        "💻 Студент"
    ]

    if message.text not in levels:

        await message.answer(
            "Сначала пройдите тест на профориентацию."
        )
        return
    else:
        data = await state.get_data()
        education_level = data.get(
            "education_level",
            "Не указан"
        )

    await state.update_data(
        education_level=message.text
    )

    await state.set_state(
        CareerTest.question
    )

    await state.update_data(
        question_index=0,
        skills={
            "programming": 0,
            "security": 0,
            "analytics": 0,
            "networks": 0,
            "investigation": 0,
            "math": 0
        }
    )

    await message.answer(
        f"Вопрос 1/{len(QUESTIONS)}\n\n"
        f"{QUESTIONS[0]['text']}\n\n"
        f"Оцените, насколько каждое утверждение соответствует вам, где:\n\n1 — совсем не согласен(на);\n5 — полностью согласен(на)",
        reply_markup=rating_keyboard
    )

@dp.message(CareerTest.question)
async def process_question(
        message: Message,
        state: FSMContext
):

    if message.text not in ["1", "2", "3", "4", "5"]:
        await message.answer(
            "Пожалуйста, выберите число от 1 до 5."
        )
        return

    data = await state.get_data()

    question_index = data.get("question_index", 0)
    skills = data.get("skills")
    current_skill = QUESTIONS[question_index]["skill"]
    skills[current_skill] += int(message.text)
    question_index += 1

    # Если вопросы ещё есть
    if question_index < len(QUESTIONS):

        await state.update_data(
            question_index=question_index,
            skills=skills
        )

        await message.answer(
            f"Вопрос {question_index + 1}/{len(QUESTIONS)}\n\n"
            f"{QUESTIONS[question_index]['text']}\n\n"
            f"Оцените от 1 до 5",
            reply_markup=rating_keyboard
        )

    # Если тест завершён
    else:

        blue_score = (
                skills["security"] +
                skills["analytics"] +
                skills["investigation"]
        )

        red_score = (
                skills["security"] +
                skills["programming"] +
                skills["networks"]
        )

        if blue_score >= red_score:
            team = "Blue Team"
            team_name = "🛡️ BLUE TEAM"
            team_description = (
                "Вам ближе защитное направление кибербезопасности.\n"
                "Такие специалисты занимаются мониторингом событий безопасности, "
                "расследованием инцидентов, поиском угроз и защитой инфраструктуры.\n\n"
            )
        else:
            team = "Red Team"
            team_name = "🔴 RED TEAM"
            team_description = (
                "Вам ближе атакующее направление кибербезопасности.\n"
                "Такие специалисты ищут уязвимости, проводят тестирование на проникновение "
                "и моделируют действия злоумышленников.\n\n"
            )

        profession_scores = {}

        for profession, required_skills in PROFESSIONS[team].items():

            score = 0

            for skill in required_skills:
                score += skills.get(skill, 0)

            profession_scores[profession] = score

        sorted_professions = sorted(
            profession_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top3 = sorted_professions[:3]

        specialties = set()

        for profession, score in top3:

            if profession in SPECIALTIES:

                for specialty in SPECIALTIES[profession]:
                    specialties.add(specialty)

        result_text = (
            "🎯 Ваш профиль\n\n"
            f"💻 Программирование: {skills['programming']}\n"
            f"🛡 ИБ: {skills['security']}\n"
            f"📊 Аналитика: {skills['analytics']}\n"
            f"🌐 Сети: {skills['networks']}\n"
            f"🔎 Расследования: {skills['investigation']}\n"
            f"📐 Математика: {skills['math']}\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"{team_name}\n\n"
            f"{team_description}"
            f"🎯 Рекомендуемые профессии:\n\n"
        )

        medals = ["🥇", "🥈", "🥉"]

        for i, (profession, score) in enumerate(top3):
            result_text += f"{medals[i]} {profession}\n"

        # result_text += "\n\n🎓 Подходящие направления подготовки:\n\n"
        #
        # for specialty in specialties:
        #     result_text += f"• {specialty}\n"

        education_level = data.get(
            "education_level",
            "Не указан"
        )



        plan = build_plan(
            education_level
        )

        save_user(
            message.from_user.id,
            {
                "education_level": education_level,
                "team": team,
                "professions": [
                    top3[0][0],
                    top3[1][0],
                    top3[2][0]
                ],
                "skills": skills,
                "plan": plan
            }
        )

        await state.clear()

        await message.answer(
            result_text,
            reply_markup=menu
        )

        education_level = data.get(
            "education_level",
            "Не указан"
        )



@dp.message(CareerTest.mentor_chat)
async def mentor_chat(
        message: Message,
        state: FSMContext
):

    user = get_user(
        message.from_user.id
    )

    if not user:

        await message.answer(
            "Сначала пройдите профориентацию."
        )
        return

    if user["requests_left"] <= 0:

        await message.answer(
            "❌ Лимит запросов к ИИ исчерпан.\n\n"
            "Попробуйте позже или обратитесь к администратору."
        )
        return

    await message.answer(
        "🤖 Думаю над ответом..."
    )

    answer = ask_ai(
        user,
        message.text
    )

    user["requests_left"] -= 1

    save_user(
        message.from_user.id,
        user
    )

    await message.answer(
        f"{answer}\n\n"
        f"━━━━━━━━━━━━\n"
        f"🤖 Осталось запросов: {user['requests_left']}"
    )



@dp.message(F.text == "🗺️ Моя карьерная траектория")
async def month_plan_start(
        message: Message,
        state: FSMContext
):

    user = get_user(
        message.from_user.id
    )

    if not user:

        await message.answer(
            "Сначала пройдите профориентацию."
        )
        return

    if "goal" not in user:

        await state.set_state(
            CareerTest.month_plan_goal
        )

        await message.answer(
            "Для какой цели сформировать план?",
            reply_markup=goal_keyboard
        )

        return

    await state.set_state(
        CareerTest.month_plan_action
    )

    await message.answer(
        f"🎯 Текущая цель:\n\n"
        f"{user['goal']}\n\n"
        f"Выберите действие:",
        reply_markup=plan_keyboard
    )

@dp.message(F.text == "📚 Ресурсы для развития")
async def resources(
        message: Message
):

    user = get_user(
        message.from_user.id
    )

    if not user:

        await message.answer(
            "Сначала пройдите профориентацию."
        )

        return

    if user["team"] == "Blue Team":

        resources = BLUE_RESOURCES

    else:

        resources = RED_RESOURCES

    text = "📚 Рекомендуемые ресурсы\n\n"

    text += "📖 Книги:\n"

    for book in resources["books"]:
        text += f"• {book}\n"

    text += "\n💻 Практика:\n"

    for platform in resources["practice"]:
        text += f"• {platform}\n"

    text += "\n📂 Каналы:\n"

    for channel in resources["telegram"]:
        text += f"• {channel}\n"

    await message.answer(text)

@dp.message(F.text == "👤 Мой профиль")
async def profile(message: Message):

    user = get_user(
        message.from_user.id
    )
    print(user)

    if not user:

        await message.answer(
            "Сначала пройдите профориентацию."
        )
        return

    professions = ", ".join(
        user["professions"]
    )

    plan_text = ""

    for item in user["plan"]:
        plan_text += f"• {item}\n"

    goal = user.get(
        "goal",
        "Не выбрана"
    )

    professions = "\n".join(
        f"• {profession}" for profession in user["professions"]
    )

    plan_text = "\n".join(
        f"• {item}" for item in user["plan"]
    )

    goal = user.get(
        "goal",
        "Не выбрана"
    )

    requests = user.get(
        "requests_left",
        20
    )

    await message.answer(
        f"👤 Ваш профиль\n\n"

        f"🎓 Статус\n"
        f"{user['education_level']}\n\n"

        f"🛡 Направление\n"
        f"{user['team']}\n\n"

        f"💼 Подходящие профессии\n"
        f"{professions}\n\n"

        f"🎯 Цель\n"
        f"{goal}\n\n"

        f"🚀 Базовая траектория\n"
        f"{plan_text}\n\n"

        f"🤖 Осталось запросов к наставнику\n"
        f"{requests} / 20"
    )

@dp.message(F.text == "🗺️ Моя карьерная траектория")
async def month_plan_start(
        message: Message,
        state: FSMContext
):

    user = get_user(
        message.from_user.id
    )

    if not user:

        await message.answer(
            "Сначала пройдите профориентацию."
        )
        return

    if "goal" not in user:

        await state.set_state(
            CareerTest.month_plan_goal
        )

        await message.answer(
            "Для какой цели сформировать план?",
            reply_markup=goal_keyboard
        )

        return

    await state.set_state(
        CareerTest.month_plan_action
    )

    await message.answer(
        f"🎯 Текущая цель:\n\n"
        f"{user['goal']}\n\n"
        f"Выберите действие:",
        reply_markup=plan_keyboard
    )

@dp.message(CareerTest.month_plan_action)
async def plan_actions(
        message: Message,
        state: FSMContext
):

    user = get_user(
        message.from_user.id
    )

    if message.text == "🗺️ Показать траекторию":

        if "month_plan" not in user:

            await message.answer(
                "План пока не сформирован."
            )

            return

        await message.answer(
            user["month_plan"]
        )

        return

    if message.text == "🔄 Изменить цель":

        await state.set_state(
            CareerTest.month_plan_goal
        )

        await message.answer(
            "Выберите новую цель:",
            reply_markup=goal_keyboard
        )

        return




@dp.message(CareerTest.month_plan_goal)
async def process_goal(
        message: Message,
        state: FSMContext
):

    if message.text not in GOALS:

        await message.answer(
            "Выберите цель кнопкой."
        )
        return

    user = get_user(
        message.from_user.id
    )


    user["goal"] = message.text

    await message.answer(
        "⏳ Формирую персональный план..."
    )

    plan = generate_month_plan(user)

    user["month_plan"] = plan

    if not plan:
        await message.answer(
            "Ошибка генерации плана."
        )

        return

    save_user(
        message.from_user.id,
        user
    )

    await state.clear()

    await message.answer(
        plan,
        reply_markup=menu
    )

@dp.message()
async def unknown_message(message: Message):
    await message.answer(
        "Выберите пункт меню.",
        reply_markup=menu
    )


# =========================
# Запуск бота
# =========================

if __name__ == "__main__":
    dp.run_polling(bot)