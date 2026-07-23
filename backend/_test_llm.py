import traceback
from app.core.llm.factory import get_llm

try:
    llm = get_llm('classifier')
    print(f'Model: {llm.model_name}')
    print(f'Base URL: {llm.openai_api_base if hasattr(llm, "openai_api_base") else "?"}')
    print('Invoking...')
    resp = llm.invoke('Say hello in one word')
    print(f'Response: {resp.content[:200]}')
except Exception:
    traceback.print_exc()
