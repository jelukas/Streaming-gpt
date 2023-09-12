from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import openai
import asyncio
from django.views.decorators.http import require_POST
from django.http import HttpResponse, StreamingHttpResponse
from chat.api_keys import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY

# Create your views here.
def home(request):
    return render(request, "chatin/home.html")


def advanced_home(request):
    return render(request, "chatin/advanced.html")


def send(request):
    return HttpResponse("hey ! aquí estoy")


@csrf_exempt
@require_POST
def stream_response(request):
    async def content_generator():
        yield "Esperando contenido...\n"
        # Aquí puedes simular un delay o agregar cualquier lógica que quieras
        # Por ahora, solo enviaré un mensaje después de "esperar"
        await asyncio.sleep(3)
        yield "¡Respuesta de ChatGPT!"
        await asyncio.sleep(3)
        yield "¡Respuesta de ChatGPT!"
        await asyncio.sleep(3)
        yield "¡Respuesta de ChatGPT!"
        await asyncio.sleep(3)
        yield "¡Respuesta de ChatGPT!"

    return StreamingHttpResponse(content_generator(), content_type='text/plain')


@csrf_exempt
@require_POST
def chatgpt_stream_response(request):
    async def content_generator():
        completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un cachondo mental y solo sabes hacer bromas... cualqeuir cosa que te digan te la tomas a broma y respondessacarticamente y con otra broma."},
            {"role": "user", "content": request.POST.get("message")}
        ],
        stream=True
        )
        for chunk in completion:
            delta_content = chunk.choices[0].delta.get('content', None)
            if delta_content:
                yield (str(delta_content))
    return StreamingHttpResponse(content_generator(), content_type='text/plain')


@csrf_exempt
@require_POST
def advanced_chatgpt_stream_response(request):
    async def content_generator():

        # Iniciar con el mensaje del sistema si no hay mensajes previos
        if "messages" not in request.session:
            request.session["messages"] = [{"role": "system", "content": "Eres un asistente muy inteligente y te gusta ayudar a la gente."}]

        # Añadir el mensaje del usuario
        request.session["messages"].append({"role": "user", "content": request.POST.get("message")})

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=request.session["messages"],
            stream=True
        )

        new_message = ''

        for chunk in completion:
            delta_content = chunk.choices[0].delta.get('content', None)
            if delta_content:
                new_message += str(delta_content)
                yield (str(delta_content))

        request.session["messages"].append({"role": "assistant", "content": new_message})
        request.session.modified = True  # Importante para asegurar que se guarden los cambios en la sesión
        print(request.session["messages"])

    return StreamingHttpResponse(content_generator(), content_type='text/plain')
