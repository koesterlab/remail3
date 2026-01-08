import enum


import enum

class LLMModel(enum.Enum):
    GPT_4_0314 = "gpt-4-0314"  # existiert, muss zu FunctionCallingLLM gewrappt werden
    GPT_4_32K_0314 = "gpt-4-32k-0314"  # existiert, FunctionCalling nötig
    TEXT_DAVINCI_003 = "text-davinci-003"  # existiert, FunctionCalling nötig
    TEXT_DAVINCI_002 = "text-davinci-002"  # existiert, FunctionCalling nötig
    GPT_3_5_TURBO_0301 = "gpt-3.5-turbo-0301"  # existiert, FunctionCalling nötig
    GPT_3_5_TURBO_INSTRUCT = "gpt-3.5-turbo-instruct"  # existiert, FunctionCalling nötig
    TEXT_ADA_001 = "text-ada-001"  # existiert, FunctionCalling nötig
    TEXT_BABBAGE_001 = "text-babbage-001"  # existiert, FunctionCalling nötig
    TEXT_CURIE_001 = "text-curie-001"  # existiert, FunctionCalling nötig
    ADA = "ada"  # existiert, FunctionCalling nötig
    BABBAGE = "babbage"  # existiert, FunctionCalling nötig
    CURIE = "curie"  # existiert, FunctionCalling nötig
    DAVINCI = "davinci"  # existiert, FunctionCalling nötig