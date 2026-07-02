from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from config import ADMIN_ID

from utils.ctf_storage import (
    save_ctf_registration,
    get_ctf_users,
    is_ctf_registered
)

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from states.ctf import (
    CTFRegistration,
    AdminBroadcast
)
from data.ctf import CTF_INFO


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
        [KeyboardButton(text="🏆 Мероприятия")],
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
    if message.from_user.id == ADMIN_ID:

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎯 Профориентация")],
                [KeyboardButton(text="🗺️ Моя карьерная траектория")],
                [KeyboardButton(text="🏆 Мероприятия")],
                [KeyboardButton(text="👤 Мой профиль")],
                [KeyboardButton(text="⚙️ Панель администратора")]
            ],
            resize_keyboard=True
        )

    else:

        keyboard = menu

    await message.answer(
        "Привет! Я CyberMentor 👋\n\nЯ — интеллектуальный карьерный наставник, который помогает школьникам, абитуриентам и студентам построить профессиональную траекторию в сфере кибербезопасности и IT.\n\nВместе мы определим подходящее направление, сформируем карьерную траекторию и подберём ресурсы для развития.",
        reply_markup=keyboard
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

@dp.message(F.text == "📊 Статистика")
async def ctf_stats(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    users = get_ctf_users()

    await message.answer(
        f"📊 Статистика\n\n"
        f"👥 Зарегистрировано участников:\n\n"
        f"{len(users)}"
    )

@dp.message(F.text == "📢 Рассылка")
async def start_broadcast(
        message: Message,
        state: FSMContext
):

    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(
        AdminBroadcast.message
    )

    await message.answer(
        "Введите текст сообщения для всех участников:"
    )

@dp.message(AdminBroadcast.message)
async def send_broadcast(
        message: Message,
        state: FSMContext
):

    users = get_ctf_users()

    success = 0

    for user in users.values():

        try:

            await bot.send_message(
                user["telegram_id"],
                f"📢 Сообщение от организаторов\n\n{message.text}"
            )

            success += 1

        except:

            pass

    await state.clear()

    await message.answer(
        f"✅ Рассылка завершена.\n\n"
        f"Сообщение получили {success} участников.",
        reply_markup=admin_menu
    )

@dp.message(F.text == "🔗 Отправить ссылку")
async def start_send_link(
        message: Message,
        state: FSMContext
):

    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(
        AdminBroadcast.link
    )

    await message.answer(
        "Отправьте ссылку на платформу CTF:"
    )

@dp.message(AdminBroadcast.link)
async def send_ctf_link(
        message: Message,
        state: FSMContext
):

    users = get_ctf_users()

    success = 0
    failed = 0

    for user in users.values():

        try:

            await bot.send_message(
                chat_id=user["telegram_id"],
                text=(
                    "🏆 Онлайн CTF начинается!\n\n"
                    "Переходите на платформу по ссылке:\n\n"
                    f"{message.text}\n\n"
                    "Желаем удачи! 🚀"
                )
            )

            success += 1

        except Exception:
            failed += 1

    await state.clear()

    await message.answer(
        "✅ Ссылка успешно отправлена!\n\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Не доставлено: {failed}",
        reply_markup=admin_menu
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


@dp.message(F.text == "🏆 Мероприятия")
async def ctf_menu(message: Message):

    users = get_ctf_users()

    if str(message.from_user.id) in users:

        await message.answer(
            "🏆 Онлайн CTF\n\n"
            "✅ Вы уже зарегистрированы.\n\n"
            "Перед началом соревнования мы отправим:\n"
            "• напоминание;\n"
            "• ссылку на платформу;\n"
            "• организационную информацию."
        )

        return
    else:
        await message.answer(
            f"""
    🏆 {CTF_INFO['title']}
    
    📅 Дата:
    {CTF_INFO['date']}
    
    🕒 Время:
    {CTF_INFO['time']}
    
    🚀 Важно!
    {CTF_INFO['duration']}
    
    Для участия нажмите кнопку 📝 Зарегистрироваться
    """,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📝 Зарегистрироваться")],
                    [KeyboardButton(text="🏠 Главное меню")]
                ],
                resize_keyboard=True
            )
        )


@dp.message(F.text == "📝 Зарегистрироваться")
async def start_ctf_registration(
        message: Message,
        state: FSMContext
):

    if is_ctf_registered(message.from_user.id):
        await message.answer(
            "✅ Вы уже зарегистрированы на CTF!"
        )

        return

    await state.set_state(
        CTFRegistration.full_name
    )

    await message.answer(
        "Введите ваши ФИО:"
    )

@dp.message(CTFRegistration.full_name)
async def ctf_name(
        message: Message,
        state: FSMContext
):

    await state.update_data(
        full_name=message.text
    )

    await state.set_state(
        CTFRegistration.organization
    )

    await message.answer(
        "Введите название образовательной организации:"
    )

@dp.message(CTFRegistration.organization)
async def ctf_org(
        message: Message,
        state: FSMContext
):

    await state.update_data(
        organization=message.text
    )

    await state.set_state(
        CTFRegistration.course
    )

    await message.answer(
        "Укажите курс или класс:"
    )

@dp.message(CTFRegistration.course)
async def ctf_course(
        message: Message,
        state: FSMContext
):

    await state.update_data(
        course=message.text
    )

    await state.set_state(
        CTFRegistration.email
    )

    await message.answer(
        "Введите адрес электронной почты:"
    )

@dp.message(CTFRegistration.email)
async def ctf_email(
        message: Message,
        state: FSMContext
):

    data = await state.get_data()

    registration = {
        "telegram_id": message.from_user.id,
        "full_name": data["full_name"],
        "organization": data["organization"],
        "course": data["course"],
        "email": message.text,
        "registered": True
    }

    save_ctf_registration(
        message.from_user.id,
        registration
    )

    await state.clear()

    await message.answer(
        "🎉 Вы успешно зарегистрированы на онлайн CTF!\n\n"
        "Спасибо за регистрацию.\n\n"
        "Перед началом соревнования вы получите:\n"
        "⏰ Напоминание о старте\n"
        "🔗 Ссылку на платформу\n"
        "📢 Важные организационные сообщения\n\n"
        "До встречи на соревновании! 🚀",
        reply_markup=menu
    )

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="🔗 Отправить ссылку")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)

@dp.message(F.text == "⚙️ Панель администратора")
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "⚙️ Панель администратора",
        reply_markup=admin_menu
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