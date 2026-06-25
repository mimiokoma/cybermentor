from openai import OpenAI
from config import OPENAI_API_KEY
from agent.promts import SYSTEM_PROMPT, MONTH_PLAN_PROMPT, PROGRESS_PROMPT

client = OpenAI(
    api_key=OPENAI_API_KEY
)

def ask_ai(user_profile, question):

    profile = f"""
Профиль пользователя

Статус:
{user_profile.get("education_level", "Не указан")}

Направление:
{user_profile.get("team", "Не определено")}

Подходящие профессии:
{", ".join(user_profile.get("professions", []))}

Цель:
{user_profile.get("goal", "Не выбрана")}

Текущий план:
{chr(10).join(user_profile.get("plan", []))}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
{profile}

====================

Вопрос пользователя:

{question}

====================

Отвечай с учетом профиля пользователя.
Не повторяй профиль в ответе.
Дай максимально практические рекомендации.
"""
            }
        ]
    )

    return response.choices[0].message.content

def generate_month_plan(user_profile):

    profile_text = f"""
Статус: {user_profile.get('education_level')}

Направление: {user_profile.get('team')}

Цель: {user_profile.get('goal')}

Профессии:
{", ".join(user_profile.get('professions', []))}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.8,
        messages=[
            {
                "role": "system",
                "content": MONTH_PLAN_PROMPT
            },
            {
                "role": "user",
                "content": profile_text
            }
        ]
    )
    return response.choices[0].message.content


def analyze_progress(user, progress):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.8,
        messages=[
            {
                "role": "system",
                "content": PROGRESS_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Профиль:

{user}

Новый прогресс:

{progress}
"""
            }
        ]
    )
    return response.choices[0].message.content
