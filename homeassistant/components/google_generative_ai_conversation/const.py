"""Constants for the Google Generative AI Conversation integration."""

import logging

DOMAIN = "google_generative_ai_conversation"
LOGGER = logging.getLogger(__package__)
CONF_PROMPT = "prompt"

ATTR_MODEL = "model"
CONF_RECOMMENDED = "recommended"
CONF_CHAT_MODEL = "chat_model"
RECOMMENDED_CHAT_MODEL = "models/gemini-2.0-flash"
RECOMMENDED_TTS_MODEL = "gemini-2.5-flash-preview-tts"
CONF_TEMPERATURE = "temperature"
RECOMMENDED_TEMPERATURE = 1.0
CONF_TOP_P = "top_p"
RECOMMENDED_TOP_P = 0.95
CONF_TOP_K = "top_k"
RECOMMENDED_TOP_K = 64
CONF_MAX_TOKENS = "max_tokens"
RECOMMENDED_MAX_TOKENS = 1500
CONF_HARASSMENT_BLOCK_THRESHOLD = "harassment_block_threshold"
CONF_HATE_BLOCK_THRESHOLD = "hate_block_threshold"
CONF_SEXUAL_BLOCK_THRESHOLD = "sexual_block_threshold"
CONF_DANGEROUS_BLOCK_THRESHOLD = "dangerous_block_threshold"
RECOMMENDED_HARM_BLOCK_THRESHOLD = "BLOCK_MEDIUM_AND_ABOVE"
CONF_USE_GOOGLE_SEARCH_TOOL = "enable_google_search_tool"
RECOMMENDED_USE_GOOGLE_SEARCH_TOOL = False

TIMEOUT_MILLIS = 10000
FILE_POLLING_INTERVAL_SECONDS = 0.05
