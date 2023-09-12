import openai
import asyncio
import uuid
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, StreamingHttpResponse
from chat.api_keys import OPENAI_API_KEY
from chatin.models import Chat


openai.api_key = OPENAI_API_KEY

# Create your views here.
def home(request):
    return render(request, "chatin/home.html")


def advanced_home(request):
    chat_uuid = uuid.uuid4()  # Genera un nuevo UUID
    return render(request, "chatin/advanced.html", {'chat_uuid': chat_uuid})


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
        chat_uuid = request.POST.get("chat_uuid")
        
        chat_history = []
        try:
            chat_obj = Chat.objects.get(uuid=chat_uuid)
            chat_history = chat_obj.conversation
        except Chat.DoesNotExist:
            chat_obj = None

        if not chat_history:
            chat_history = [{"role": "system", "content": "Eres un asistente muy inteligente y te gusta ayudar a la gente."}]
        chat_history.append({"role": "user", "content": request.POST.get("message")})

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=chat_history,
            stream=True
        )

        new_message = ''
        for chunk in completion:
            delta_content = chunk.choices[0].delta.get('content', None)
            if delta_content:
                new_message += str(delta_content)
                yield (str(delta_content))

        chat_history.append({"role": "assistant", "content": new_message})

        if chat_obj:
            chat_obj.conversation = chat_history
            chat_obj.save(update_fields=["conversation"])
        else:
            Chat.objects.create(uuid=chat_uuid, conversation=chat_history)

    return StreamingHttpResponse(content_generator(), content_type='text/plain')
