
(venv) ┌<▸> ~/g/langgraph-chatbot 
└➤ poetry install                                    
Installing dependencies from lock file

No dependencies to install or update

Installing the current project: langgraph-chatbot (0.1.0)
Warning: The current project could not be installed: [Errno 2] No such file or directory: '/Users/aironman/git/langgraph-chatbot/README.md'
If you do not want to install the current project use --no-root.
If you want to use Poetry only for dependency management but not for packaging, you can disable package mode by setting package-mode = false in your pyproject.toml file.
In a future version of Poetry this warning will become an error!
┌<▸> ~/g/langgraph-chatbot 
└➤ poetry shell                 
Spawning shell within /Users/aironman/git/interactive-llm-voice-a/venv
┌<▸> ~/g/langgraph-chatbot 
└➤ emulate bash -c '. /Users/aironman/git/interactive-llm-voice-a/venv/bin/activate'

(venv) ┌<▸> ~/g/langgraph-chatbot 
└➤ poetry run python test-sample-claude-sonnet-bot.py
Bienvenido al chatbot. Escribe 'salir' para terminar.
Tú: quien eres?
Bot: Soy un asistente virtual creado por Anthropic. Soy un sistema de inteligencia artificial entrenado para ayudar a los humanos con una amplia variedad de tareas. Puedo conversar en lenguaje natural, responder preguntas, brindar explicaciones y asistencia en áreas como investigación, redacción, análisis de datos y mucho más. Mi objetivo es ser útil y amigable. ¿En qué puedo ayudarte hoy?
Tú: salir
(venv) ┌<▸> ~/g/langgraph-chatbot 
└➤ poetry run python test-bot.py                     
The capital of France is Paris.
(venv) ┌<▸> ~/g/langgraph-chatbot 
└➤ 

