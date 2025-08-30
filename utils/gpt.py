import openai, os
openai.api_key = os.getenv('OPENAI_API_KEY')
def generar_respuesta(prompt):
 return openai.ChatCompletion.create(
  model='gpt-4o',
  messages=[
    {"role": "system", "content": "Eres Lia: espontánea, sensual, directa, femenina y muy cariñosa."},
    {"role": "user", "content": prompt}
  ]
 )['choices'][0]['message']['content']
