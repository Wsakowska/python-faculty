"""Widoki aplikacji ai_assistant — Asystent kucharski AI."""

import google.generativeai as genai

from django.shortcuts import render
from django.conf import settings


def ai_chat(request):
    """Asystent kucharski — generuje przepis na podstawie składników."""
    response_text = None
    user_message = ''
    error = None

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            error = 'Wpisz składniki lub pytanie!'
        elif not settings.GEMINI_API_KEY:
            error = 'Brak klucza API Gemini. Dodaj GEMINI_API_KEY do pliku .env.'
        else:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-pro')

                prompt = f"""Jesteś asystentem kucharskim w aplikacji "Co mam w lodówce?".
Użytkownik poda Ci składniki lub zapyta o przepis.
Odpowiadaj ZAWSZE po polsku.
Podaj konkretny przepis z:
- Nazwą dania
- Listą składników z ilościami
- Instrukcją krok po kroku
- Czasem przygotowania
- Poziomem trudności (łatwy/średni/trudny)

Bądź przyjazny i kreatywny!

Użytkownik napisał: {user_message}"""

                result = model.generate_content(prompt)
                response_text = result.text

            except Exception as e:
                error = f'Błąd połączenia z AI: {str(e)}'

    return render(request, 'ai_assistant/chat.html', {
        'response_text': response_text,
        'user_message': user_message,
        'error': error,
    })