El repositorio incluye pocs sobre como usar indices optimizados para cargar ficheros pdf de alta calidad, o al menos espero que se preocupe de cargar pdf de alta calidad para que así el RAG al hacer busqueda vectorial seleccione vectores verdaderamente relevantes y verosimiles, en vez de información similar, que es el gran problema actual que afronta esta tecnología. Hay ejemplos con ChromaDB y FAISS. ChromaDB está menos maduro, en mi opinión que el resto de bases de datos vectoriales, pues no incluye, aún, indices avanzados. FAISS si los incluye y ademas está optimizado para correr con soporte de GPUs y se puede instalar on-premise. Personalmente me gusta más el on-premise porque el el cloud acaba atando al cliente y a los ingenieros pues tenemos que gastar mucho dinero en formarnos en tecnología propietaria.

# Como empezar

  poetry install                                    
  poetry shell                 

# En este punto ya tenemos cargado el entorno virtual...

  poetry run python test-sample-claude-sonnet-bot.py

  Bienvenido al chatbot. Escribe 'salir' para terminar.
  Tú: quien eres?
  Bot: Soy un asistente virtual creado por Anthropic. Soy un sistema de inteligencia artificial entrenado para ayudar a los humanos con una amplia variedad de tareas. Puedo conversar en lenguaje natural, responder preguntas, brindar explicaciones y asistencia en áreas como investigación, redacción, análisis de datos y mucho más. Mi objetivo es ser útil y amigable. ¿En qué puedo ayudarte hoy?
  Tú: salir

  poetry run python test-bot.py                     

  The capital of France is Paris.

